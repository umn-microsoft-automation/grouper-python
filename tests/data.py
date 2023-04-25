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

find_groups_result_valid_one_group = {
    "WsFindGroupsResults": {
        "resultMetadata": {
            "success": "T",
        },
        "groupResults": [grouper_group_result1],
    }
}
