URI_BASE = "https://grouper/grouper-ws/servicesRest/v2_4_000"

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
    "displayExtension": "Test1 Display Name",
    "name": "test:GROUP1",
    "typeOfGroup": "group",
    "idIndex": "12345",
}

find_groups_result_valid_one_group = {
    "WsFindGroupsResults": {
        "resultMetadata": {"success": "T"},
        "groupResults": [grouper_group_result1],
    }
}

find_groups_result_valid_two_groups = {
    "WsFindGroupsResults": {
        "resultMetadata": {"success": "T"},
        "groupResults": [grouper_group_result1, grouper_group_result2],
    }
}

get_subject_result_valid = {
    "WsGetSubjectsResults": {
        "resultMetadata": {"success": "T"},
        "subjectAttributeNames": ["name", "description"],
        "wsSubjects": [
            {
                "sourceId": "ldap",
                "success": "T",
                "attributeValues": ["User 3 Name", "username3"],
                "name": "User 3 Name",
                "id": "12345abcd",
            }
        ],
    }
}

find_stem_result_valid = {
    "WsFindStemsResults": {
        "resultMetadata": {"success": "T"},
        "stemResults": [
            {
                "displayExtension": "Child Stem",
                "extension": "child",
                "displayName": "Test Stem:Child Stem",
                "name": "test:child",
                "description": "a child stem",
                "idIndex": "452945",
                "uuid": "e2c91c056fb746cca551d6887c722215",
            }
        ],
    }
}
