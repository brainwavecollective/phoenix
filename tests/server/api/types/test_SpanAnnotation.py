from datetime import datetime

import pytest
from phoenix.db import models
from phoenix.server.api.types.node import from_global_id_with_expected_type
from sqlalchemy import insert, select
from strawberry.relay import GlobalID


@pytest.fixture
async def project_with_a_single_trace_and_span(session) -> None:
    """
    Contains a project with a single trace and a single span.
    """
    project_row_id = await session.scalar(
        insert(models.Project).values(name="project-name").returning(models.Project.id)
    )
    trace_id = await session.scalar(
        insert(models.Trace)
        .values(
            trace_id="1",
            project_rowid=project_row_id,
            start_time=datetime.fromisoformat("2021-01-01T00:00:00.000+00:00"),
            end_time=datetime.fromisoformat("2021-01-01T00:01:00.000+00:00"),
        )
        .returning(models.Trace.id)
    )
    await session.execute(
        insert(models.Span)
        .values(
            trace_rowid=trace_id,
            span_id="1",
            parent_id=None,
            name="chain span",
            span_kind="CHAIN",
            start_time=datetime.fromisoformat("2021-01-01T00:00:00.000+00:00"),
            end_time=datetime.fromisoformat("2021-01-01T00:00:30.000+00:00"),
            attributes={
                "input": {"value": "chain-span-input-value", "mime_type": "text/plain"},
                "output": {"value": "chain-span-output-value", "mime_type": "text/plain"},
            },
            events=[],
            status_code="OK",
            status_message="okay",
            cumulative_error_count=0,
            cumulative_llm_token_count_prompt=0,
            cumulative_llm_token_count_completion=0,
        )
        .returning(models.Span.id)
    )


async def test_annotating_a_span(
    session, test_client, project_with_a_single_trace_and_span
) -> None:
    span_gid = GlobalID("Span", "1")
    response = await test_client.post(
        "/graphql",
        json={
            "query": """
                mutation AddSpanAnnotation($input: [CreateSpanAnnotationInput!]!) {
                    createSpanAnnotations(input: $input) {
                        spanAnnotations {
                            id
                            spanId
                            name
                            annotatorKind
                            label
                            score
                            explanation
                            metadata
                        }
                    }
                }
            """,
            "variables": {
                "input": [
                    {
                        "spanId": str(span_gid),
                        "name": "Test Annotation",
                        "annotatorKind": "HUMAN",
                        "label": "True",
                        "score": 0.95,
                        "explanation": "This is a test annotation.",
                        "metadata": {},
                    }
                ]
            },
        },
    )

    data = response.json()["data"]
    annotation_gid = GlobalID.from_id(data["createSpanAnnotations"]["spanAnnotations"][0]["id"])
    annotation_id = from_global_id_with_expected_type(annotation_gid, "SpanAnnotation")
    orm_annotation = await session.scalar(
        select(models.SpanAnnotation).where(models.SpanAnnotation.id == annotation_id)
    )
    assert orm_annotation.name == "Test Annotation"
    assert orm_annotation.annotator_kind == "HUMAN"
    assert orm_annotation.label == "True"
    assert orm_annotation.score == 0.95
    assert orm_annotation.explanation == "This is a test annotation."
    assert orm_annotation.metadata_ == dict()

    response = await test_client.post(
        "/graphql",
        json={
            "query": """
                mutation PatchSpanAnnotation($input: [PatchAnnotationInput!]!) {
                    patchSpanAnnotations(input: $input) {
                        spanAnnotations {
                            id
                            name
                            annotatorKind
                            label
                            score
                            explanation
                            metadata
                        }
                    }
                }
            """,
            "variables": {
                "input": [
                    {
                        "annotationId": str(annotation_gid),
                        "name": "Updated Annotation",
                        "annotatorKind": "HUMAN",
                        "label": "Positive",
                        "score": 0.95,
                        "explanation": "Updated explanation",
                        "metadata": {"updated": True},
                    }
                ]
            },
        },
    )

    orm_annotation = await session.scalar(
        select(models.SpanAnnotation).where(models.SpanAnnotation.id == annotation_id)
    )
    assert orm_annotation.name == "Updated Annotation"
    assert orm_annotation.label == "Positive"
    assert orm_annotation.explanation == "Updated explanation"
    assert orm_annotation.metadata_ == {"updated": True}

    response = await test_client.post(
        "/graphql",
        json={
            "query": """
                mutation DeleteSpanAnnotation($input: DeleteAnnotationsInput!) {
                    deleteSpanAnnotations(input: $input) {
                        spanAnnotations {
                            id
                            name
                            annotatorKind
                            label
                            score
                            explanation
                            metadata
                        }
                    }
                }
            """,
            "variables": {
                "input": {
                    "annotationIds": [str(annotation_gid)],
                }
            },
        },
    )

    orm_annotation = await session.scalar(
        select(models.SpanAnnotation).where(models.SpanAnnotation.id == annotation_id)
    )
    assert not orm_annotation
