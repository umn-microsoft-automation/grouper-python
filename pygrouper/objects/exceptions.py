from typing import Any


class GrouperException(Exception):
    """Base Exception for all Grouper Exceptions."""

    pass


class GrouperSuccessException(GrouperException):
    """Grouper call was not succesful or unexpected data returned."""

    def __init__(self, grouper_result: dict[str, Any]) -> None:
        """Initialize Exception with Grouper result body."""
        self.grouper_result = grouper_result
        super().__init__(self.grouper_result)


class GrouperAuthException(GrouperException):
    """Issue authenticating to Grouper."""

    pass


class GrouperPermissionDenied(GrouperException):
    """Permission denied in grouper."""

    pass


class GrouperEntityNotFoundException(GrouperException):
    """The Grouper Entity was not found."""

    def __init__(self, entity_identifier: str) -> None:
        """Initialize Exception with entity name."""
        self.entity_identifier = entity_identifier
        super().__init__(f"{self.entity_identifier} not found")


class GrouperSubjectNotFoundException(GrouperEntityNotFoundException):
    """The Grouper Subject was not found"""

    def __init__(self, subject_identifier: str) -> None:
        """Initialize Exception with subject identifier."""
        self.subject_identifier = subject_identifier
        super().__init__(subject_identifier)


class GrouperGroupNotFoundException(GrouperEntityNotFoundException):
    """The Grouper Group was not found."""

    def __init__(self, group_name: str) -> None:
        """Initialize Exception with group name."""
        self.group_name = group_name
        super().__init__(group_name)


class GrouperStemNotFoundException(GrouperEntityNotFoundException):
    """The Grouper Stem was not found."""

    def __init__(self, stem_name: str) -> None:
        """Initialize Exception with stem name."""
        self.stem_name = stem_name
        super().__init__(stem_name)
