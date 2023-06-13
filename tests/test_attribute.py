# mypy: allow_untyped_defs
from __future__ import annotations
from grouper_python.objects import Group, Stem
from . import data
# import pytest
import respx
from httpx import Response


@respx.mock
def test_group_get_attribute_assignments_none(grouper_group: Group):
    respx.post(url=data.URI_BASE + "/attributeAssignments").mock(
        side_effect=[
            Response(200, json=data.get_attribute_assignment_result_no_assignments)
        ]
    )
    assgs = grouper_group.get_attribute_assignments_on_this()

    assert len(assgs) == 0


@respx.mock
def test_group_get_attribute_assignments(grouper_group: Group):
    respx.post(url=data.URI_BASE + "/attributeAssignments").mock(
        side_effect=[
            Response(200, json=data.get_attribute_assignment_result_group)
        ]
    )
    assgs = grouper_group.get_attribute_assignments_on_this()

    assert len(assgs) == 1


@respx.mock
def test_group_assign_attribute(grouper_group: Group):
    respx.post(url=data.URI_BASE + "/attributeAssignments").mock(
        side_effect=[
            Response(200, json=data.assign_attribute_result_group)
        ]
    )
    assgs = grouper_group.assign_attribute_on_this("assign_attr", "etc:attr")
    assert len(assgs) == 1


@respx.mock
def test_group_assign_attribute_with_value(grouper_group: Group):
    respx.post(url=data.URI_BASE + "/attributeAssignments").mock(
        side_effect=[
            Response(200, json=data.assign_attribute_result_group)
        ]
    )
    assgs = grouper_group.assign_attribute_on_this(
        "assign_attr", "etc:attr", "value", "assign_value")
    assert len(assgs) == 1


@respx.mock
def test_delete_group_attribute_assignment(grouper_group: Group):
    respx.post(url=data.URI_BASE + "/attributeAssignments").mock(
        return_value=Response(200, json=data.assign_attribute_result_group)
    )
    assgs = grouper_group.assign_attribute_on_this("assign_attr", "etc:attr")
    assert len(assgs) == 1
    # If we've gotten this far, we have an assignment that we can then delete
    assgs[0].delete()


@respx.mock
def test_stem_get_attribute_assignments(grouper_stem: Stem):
    respx.post(url=data.URI_BASE + "/attributeAssignments").mock(
        side_effect=[
            Response(200, json=data.get_attribute_assignment_result_stem)
        ]
    )
    assgs = grouper_stem.get_attribute_assignments_on_this()

    assert len(assgs) == 1


@respx.mock
def test_stem_assign_attribute(grouper_stem: Stem):
    respx.post(url=data.URI_BASE + "/attributeAssignments").mock(
        side_effect=[
            Response(200, json=data.assign_attribute_result_stem)
        ]
    )
    assgs = grouper_stem.assign_attribute_on_this("assign_attr", "etc:attr")
    assert len(assgs) == 1


@respx.mock
def test_delete_stem_attribute_assignment(grouper_stem: Stem):
    respx.post(url=data.URI_BASE + "/attributeAssignments").mock(
        return_value=Response(200, json=data.assign_attribute_result_stem)
    )
    assgs = grouper_stem.assign_attribute_on_this("assign_attr", "etc:attr")
    assert len(assgs) == 1
    # If we've gotten this far, we have an assignment that we can then delete
    assgs[0].delete()
