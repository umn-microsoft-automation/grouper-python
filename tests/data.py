URI_BASE = "https://grouper/grouper-ws/servicesRest/v2_4_000"

subject_attribute_names = ["description", "name"]

grouper_group_result1 = {
    "extension": "GROUP1",
    "displayName": "Test Stem:Test1 Display Name",
    "description": "Group 1 Test description",
    "uuid": "1ab0482715c74f51bc32822a70bf8f77",
    "enabled": "T",
    "displayExtension": "Test1 Display Name",
    "name": "test:GROUP1",
    "typeOfGroup": "group",
    "idIndex": "12345",
}

grouper_group_result2 = {
    "extension": "GROUP2",
    "displayName": "Test Stem:Test2 Display Name",
    "description": "Group 2 Test description",
    "uuid": "61db7e3435864838b039a7fce155d49c",
    "enabled": "T",
    "displayExtension": "Test2 Display Name",
    "name": "test:GROUP2",
    "typeOfGroup": "group",
    "idIndex": "12345",
}

grouper_group_result3 = {
    "extension": "GROUP3",
    "displayName": "Test Stem:Child Stem:Test3 Display Name",
    "description": "Group 3 Test description",
    "uuid": "61db7e3435864838b039a7fce155d49c",
    "enabled": "T",
    "displayExtension": "Test3 Display Name",
    "name": "test:child:GROUP3",
    "typeOfGroup": "group",
    "idIndex": "12345",
}

find_groups_result_valid_one_group_1 = {
    "WsFindGroupsResults": {
        "resultMetadata": {"success": "T"},
        "groupResults": [grouper_group_result1],
    }
}

find_groups_result_valid_one_group_2 = {
    "WsFindGroupsResults": {
        "resultMetadata": {"success": "T"},
        "groupResults": [grouper_group_result2],
    }
}

find_groups_result_valid_one_group_3 = {
    "WsFindGroupsResults": {
        "resultMetadata": {"success": "T"},
        "groupResults": [grouper_group_result3],
    }
}

find_groups_result_valid_two_groups = {
    "WsFindGroupsResults": {
        "resultMetadata": {"success": "T"},
        "groupResults": [grouper_group_result1, grouper_group_result2],
    }
}

find_groups_result_stem_not_found = {
    "WsFindGroupsResults": {
        "resultMetadata": {
            "success": "F",
            "resultCode": "INVALID_QUERY",
            "resultMessage": "Cant find stem: 'invalid',",
        }
    }
}

find_groups_result_valid_no_groups = {
    "WsFindGroupsResults": {"resultMetadata": {"success": "T"}}
}

grouper_stem_1 = {
    "displayExtension": "Child Stem",
    "extension": "child",
    "displayName": "Test Stem:Child Stem",
    "name": "test:child",
    "description": "a child stem",
    "idIndex": "452945",
    "uuid": "e2c91c056fb746cca551d6887c722215",
}

grouper_stem_2 = {
    "displayExtension": "Second Child Stem",
    "extension": "second",
    "displayName": "Test Stem:Child Stem:Second Child Stem",
    "name": "test:child:second",
    "description": "a second child stem",
    "idIndex": "452945",
    "uuid": "359ecba27d704e58841e26fcbb3bfca8",
}

find_stem_result_valid_1 = {
    "WsFindStemsResults": {
        "resultMetadata": {"success": "T"},
        "stemResults": [grouper_stem_1],
    }
}

find_stem_result_valid_2 = {
    "WsFindStemsResults": {
        "resultMetadata": {"success": "T"},
        "stemResults": [grouper_stem_2],
    }
}

find_stem_result_valid_empty = {
    "WsFindStemsResults": {
        "resultMetadata": {"success": "T"},
        "stemResults": [],
    }
}

ws_membership1 = {
    "membershipType": "immediate",
    "groupId": "1ab0482715c74f51bc32822a70bf8f77",
    "subjectId": "61db7e3435864838b039a7fce155d49c",
    "subjectSourceId": "g:gsa",
}
ws_membership2 = {
    "membershipType": "effective",
    "groupId": "1ab0482715c74f51bc32822a70bf8f77",
    "subjectId": "abcdefgh1",
    "subjectSourceId": "ldap",
}
ws_membership3 = {
    "membershipType": "immediate",
    "groupId": "1ab0482715c74f51bc32822a70bf8f77",
    "subjectId": "abcdefgh2",
    "subjectSourceId": "ldap",
}
ws_membership4 = {
    "membershipType": "effective",
    "groupId": "1ab0482715c74f51bc32822a70bf8f77",
    "subjectId": "abcdefgh3",
    "subjectSourceId": "ldap",
}
ws_membership5 = {
    "membershipType": "immediate",
    "groupId": "1ab0482715c74f51bc32822a70bf8f77",
    "subjectId": "abcdefgh3",
    "subjectSourceId": "ldap",
}
ws_subject1 = {
    "sourceId": "g:gsa",
    "attributeValues": ["Group 2 Test description", "test:GROUP2"],
    "name": "test:GROUP2",
    "id": "61db7e3435864838b039a7fce155d49c",
}
ws_subject2 = {
    "sourceId": "ldap",
    "attributeValues": ["user1111", "User 1 Name"],
    "name": "User 1 Name",
    "id": "abcdefgh1",
}
ws_subject3 = {
    "sourceId": "ldap",
    "attributeValues": ["user2222", "User 2 Name"],
    "name": "User 2 Name",
    "id": "abcdefgh2",
}
ws_subject4 = {
    "sourceId": "ldap",
    "attributeValues": ["user3333", "User 3 Name"],
    "name": "User 3 Name",
    "id": "abcdefgh3",
}

get_subject_result_valid_person = {
    "WsGetSubjectsResults": {
        "resultMetadata": {"success": "T"},
        "subjectAttributeNames": subject_attribute_names,
        "wsSubjects": [ws_subject4 | {"success": "T"}],
    }
}

get_subject_result_valid_group = {
    "WsGetSubjectsResults": {
        "resultMetadata": {"success": "T"},
        "subjectAttributeNames": subject_attribute_names,
        "wsSubjects": [ws_subject1 | {"success": "T"}],
    }
}

get_subject_result_subject_not_found = {
    "WsGetSubjectsResults": {
        "resultMetadata": {"success": "T"},
        "wsSubjects": [{"success": "F"}],
    }
}

get_subject_result_valid_search_multiple_subjects = {
    "WsGetSubjectsResults": {
        "resultMetadata": {"success": "T"},
        "subjectAttributeNames": subject_attribute_names,
        "wsSubjects": [ws_subject1, ws_subject2, ws_subject3],
    }
}

get_subject_result_valid_search_no_results = {
    "WsGetSubjectsResults": {"resultMetadata": {"success": "T"}}
}

get_members_result_valid_one_group = {
    "WsGetMembersResults": {
        "resultMetadata": {"success": "T"},
        "subjectAttributeNames": subject_attribute_names,
        "results": [
            {
                "resultMetadata": {"success": "T"},
                "wsGroup": grouper_group_result1,
                "wsSubjects": [ws_subject1, ws_subject2],
            }
        ],
    }
}

get_members_result_empty = {
    "WsGetMembersResults": {
        "resultMetadata": {"success": "T"},
        "subjectAttributeNames": subject_attribute_names,
        "results": [
            {"resultMetadata": {"success": "T"}, "wsGroup": grouper_group_result1}
        ],
    }
}

get_members_result_group_not_found = {
    "WsGetMembersResults": {
        "resultMetadata": {"success": "F"},
        "results": [
            {
                "resultMetadata": {
                    "success": "F",
                    "resultCode": "GROUP_NOT_FOUND",
                    "resultMessage": (
                        "Invalid group for 'wsGroupLookup', "
                        "WsGroupLookup[pitGroups=[],"
                        "groupName=test:NOT,"
                    ),
                }
            }
        ],
    }
}

get_members_result_multiple_groups_second_group_not_found = {
    "WsGetMembersResults": {
        "resultMetadata": {"success": "F"},
        "results": [
            {"resultMetadata": {"success": "T"}},
            {
                "resultMetadata": {
                    "success": "F",
                    "resultCode": "GROUP_NOT_FOUND",
                    "resultMessage": (
                        "Invalid group for 'wsGroupLookup', "
                        "WsGroupLookup[pitGroups=[],"
                        "groupName=test:NOT,"
                    ),
                }
            },
        ],
    }
}

get_membership_result_valid_one_group = {
    "WsGetMembershipsResults": {
        "resultMetadata": {"success": "T"},
        "wsMemberships": [
            ws_membership1,
            ws_membership2,
            ws_membership3,
            ws_membership4,
            ws_membership5,
        ],
        "subjectAttributeNames": subject_attribute_names,
        "wsGroups": [grouper_group_result1],
        "wsSubjects": [ws_subject1, ws_subject2, ws_subject3, ws_subject4],
    }
}

get_membership_result_group_not_found = {
    "WsGetMembershipsResults": {
        "resultMetadata": {
            "success": "F",
            "resultCode": "GROUP_NOT_FOUND",
            "resultMessage": (
                "Invalid group for 'group', "
                "WsGroupLookup[pitGroups=[],"
                "groupName=test:NOT,"
            ),
        }
    }
}

get_membership_result_valid_no_memberships = {
    "WsGetMembershipsResults": {"resultMetadata": {"success": "T"}}
}

get_groups_for_subject_result_valid = {
    "WsGetMembershipsResults": {
        "resultMetadata": {"success": "T"},
        "wsGroups": [grouper_group_result1],
    }
}

get_groups_for_subject_no_memberships = {
    "WsGetMembershipsResults": {"resultMetadata": {"success": "T"}}
}

create_priv_group_request = {
    "WsRestAssignGrouperPrivilegesLiteRequest": {
        "allowed": "T",
        "privilegeName": "update",
        "subjectIdentifier": "user3333",
        "groupName": "test:GROUP1",
        "privilegeType": "access",
    }
}

delete_priv_group_request = {
    "WsRestAssignGrouperPrivilegesLiteRequest": {
        "allowed": "F",
        "privilegeName": "update",
        "subjectIdentifier": "user3333",
        "groupName": "test:GROUP1",
        "privilegeType": "access",
    }
}

assign_priv_result_valid = {
    "WsAssignGrouperPrivilegesLiteResult": {"resultMetadata": {"success": "T"}}
}

add_member_result_valid = {
    "WsAddMemberResults": {
        "resultMetadata": {"success": "T"},
        "wsGroupAssigned": grouper_group_result1,
    }
}

add_member_result_group_not_found = {
    "WsAddMemberResults": {
        "resultMetadata": {"success": "F", "resultCode": "GROUP_NOT_FOUND"}
    }
}

add_member_result_permission_denied = {
    "WsAddMemberResults": {
        "resultMetadata": {"success": "F", "resultCode": "PROBLEM_WITH_ASSIGNMENT"},
        "results": [{"resultMetadata": {"resultCode": "INSUFFICIENT_PRIVILEGES"}}],
    }
}

remove_member_result_valid = {
    "WsDeleteMemberResults": {
        "resultMetadata": {"success": "T"},
        "wsGroup": grouper_group_result1,
    }
}

has_member_result_identifier = {
    "WsHasMemberResults": {
        "resultMetadata": {"success": "T"},
        "results": [
            {
                "resultMetadata": {"success": "T", "resultCode": "IS_MEMBER"},
                "wsSubject": {"identifierLookup": "user3333"},
            }
        ],
    }
}

remove_member_result_group_not_found = {
    "WsDeleteMemberResults": {
        "resultMetadata": {"success": "F", "resultCode": "GROUP_NOT_FOUND"}
    }
}

remove_member_result_permission_denied = {
    "WsDeleteMemberResults": {
        "resultMetadata": {"success": "F", "resultCode": "PROBLEM_DELETING_MEMBERS"},
        "results": [{"resultMetadata": {"resultCode": "INSUFFICIENT_PRIVILEGES"}}],
    }
}

has_member_result_id = {
    "WsHasMemberResults": {
        "resultMetadata": {"success": "T"},
        "results": [
            {
                "resultMetadata": {"success": "T", "resultCode": "IS_MEMBER"},
                "wsSubject": {"id": "abcdefgh3"},
            }
        ],
    }
}

has_member_result_not_member = {
    "WsHasMemberResults": {
        "resultMetadata": {"success": "T"},
        "results": [
            {
                "resultMetadata": {"success": "T", "resultCode": "IS_NOT_MEMBER"},
                "wsSubject": {"id": "abcdefgh3"},
            }
        ],
    }
}

has_member_result_subject_not_found = {
    "WsHasMemberResults": {
        "resultMetadata": {"success": "T"},
        "results": [
            {
                "resultMetadata": {"success": "T", "resultCode2": "SUBJECT_NOT_FOUND"},
                "wsSubject": {"id": "abcdefgh3"},
            }
        ],
    }
}

has_member_result_group_not_found = {
    "WsHasMemberResults": {
        "resultMetadata": {"success": "F", "resultCode": "GROUP_NOT_FOUND"}
    }
}

delete_groups_result_success = {
    "WsGroupDeleteResults": {
        "resultMetadata": {"success": "T"},
        "results": [{"resultMetadata": {"resultCode": "SUCCESS"}}],
    }
}

delete_groups_permission_denied = {
    "WsGroupDeleteResults": {
        "resultMetadata": {"success": "F", "resultCode": "PROBLEM_DELETING_GROUPS"},
        "results": [{"resultMetadata": {"resultCode": "INSUFFICIENT_PRIVILEGES"}}],
    }
}

delete_groups_group_not_found = {
    "WsGroupDeleteResults": {
        "resultMetadata": {"success": "T"},
        "results": [
            {
                "resultMetadata": {
                    "resultCode": "SUCCESS_GROUP_NOT_FOUND",
                    "resultMessage": (
                        "Cant find group: 'WsGroupLookup[pitGroups=[],"
                        "groupName=test:GROUP1,"
                    ),
                }
            }
        ],
    }
}

create_priv_stem_request = {
    "WsRestAssignGrouperPrivilegesLiteRequest": {
        "allowed": "T",
        "privilegeName": "stemAttrRead",
        "subjectIdentifier": "user3333",
        "stemName": "test:child",
        "privilegeType": "naming",
    }
}

delete_priv_stem_request = {
    "WsRestAssignGrouperPrivilegesLiteRequest": {
        "allowed": "F",
        "privilegeName": "stemAttrRead",
        "subjectIdentifier": "user3333",
        "stemName": "test:child",
        "privilegeType": "naming",
    }
}

create_stems_result_success_one_stem = {
    "WsStemSaveResults": {
        "resultMetadata": {"success": "T"},
        "results": [{"wsStem": grouper_stem_2}],
    }
}

group_save_result_success_one_group = {
    "WsGroupSaveResults": {
        "resultMetadata": {"success": "T"},
        "results": [
            {"resultMetadata": {"success": "T"}, "wsGroup": grouper_group_result3}
        ],
    }
}

delete_stem_result_success = {
    "WsStemDeleteResults": {"resultMetadata": {"success": "T"}}
}

priv_result_stem = {
    "revokable": "T",
    "ownerSubject": ws_subject2,
    "allowed": "T",
    "wsStem": grouper_stem_1,
    "wsSubject": ws_subject4,
    "privilegeType": "naming",
    "privilegeName": "stemAdmin",
}

priv_result_group = {
    "revokable": "T",
    "ownerSubject": ws_subject2,
    "allowed": "T",
    "wsGroup": grouper_group_result1,
    "wsSubject": ws_subject4,
    "privilegeType": "access",
    "privilegeName": "admin",
}

get_priv_for_stem_request = {
    "WsRestGetGrouperPrivilegesLiteRequest": {
        "includeSubjectDetail": "T",
        "includeGroupDetail": "T",
        "subjectAttributeNames": "",
        "stemName": "test:child",
    }
}

get_priv_for_stem_result = {
    "WsGetGrouperPrivilegesLiteResult": {
        "resultMetadata": {"success": "T"},
        "subjectAttributeNames": subject_attribute_names,
        "privilegeResults": [priv_result_stem],
    }
}

get_priv_for_group_request = {
    "WsRestGetGrouperPrivilegesLiteRequest": {
        "includeSubjectDetail": "T",
        "includeGroupDetail": "T",
        "subjectAttributeNames": "",
        "groupName": "test:GROUP1",
    }
}

get_priv_for_group_with_subject_identifier_request = {
    "WsRestGetGrouperPrivilegesLiteRequest": {
        "includeSubjectDetail": "T",
        "includeGroupDetail": "T",
        "subjectAttributeNames": "",
        "groupName": "test:GROUP1",
        "subjectIdentifier": "user3333"
    }
}

get_priv_for_group_with_privilege_name_request = {
    "WsRestGetGrouperPrivilegesLiteRequest": {
        "includeSubjectDetail": "T",
        "includeGroupDetail": "T",
        "subjectAttributeNames": "",
        "groupName": "test:GROUP1",
        "privilegeName": "admin",
    }
}

get_priv_for_group_with_privilege_type_request = {
    "WsRestGetGrouperPrivilegesLiteRequest": {
        "includeSubjectDetail": "T",
        "includeGroupDetail": "T",
        "subjectAttributeNames": "",
        "subjectId": "abcdefgh3",
        "privilegeType": "access",
    }
}

get_priv_for_group_result = {
    "WsGetGrouperPrivilegesLiteResult": {
        "resultMetadata": {"success": "T"},
        "subjectAttributeNames": subject_attribute_names,
        "privilegeResults": [priv_result_group],
    }
}

get_priv_for_subject_request = {
    "WsRestGetGrouperPrivilegesLiteRequest": {
        "includeSubjectDetail": "T",
        "includeGroupDetail": "T",
        "subjectAttributeNames": "",
        "subjectId": "abcdefgh3",
    }
}

get_priv_for_subject_result = {
    "WsGetGrouperPrivilegesLiteResult": {
        "resultMetadata": {"success": "T"},
        "subjectAttributeNames": subject_attribute_names,
        "privilegeResults": [priv_result_stem, priv_result_group],
    }
}

get_priv_result_subject_not_found = {
    "WsGetGrouperPrivilegesLiteResult": {
        "resultMetadata": {"success": "F", "resultCode": "SUBJECT_NOT_FOUND"}
    }
}

get_priv_result_group_not_found = {
    "WsGetGrouperPrivilegesLiteResult": {
        "resultMetadata": {"success": "F", "resultCode": "GROUP_NOT_FOUND"}
    }
}

get_priv_result_stem_not_found = {
    "WsGetGrouperPrivilegesLiteResult": {
        "resultMetadata": {"success": "F", "resultCode": "STEM_NOT_FOUND"}
    }
}

get_priv_for_group_result_none_found = {
    "WsGetGrouperPrivilegesLiteResult": {"resultMetadata": {"success": "T"}}
}
