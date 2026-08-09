from app.db.models.permission import PermissionAction


PERMISSION_DEFINITIONS = {
    "creators": [
        PermissionAction.VIEW,
        PermissionAction.ADD,
        PermissionAction.EDIT,
        PermissionAction.DELETE,
    ],
}
