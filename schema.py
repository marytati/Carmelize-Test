from datetime import datetime
from typing import Any, List, Literal, Optional, Union, get_args

from pydantic import BaseModel, conint, root_validator, validator
from pydantic.utils import GetterDict

from app.worker.task_configs import (
    RunOneOffCampaignsProcesses,
    RunTemplatedCampaignsProcesses,
    TestTaskProcesses,
)

def camelize(s: str) -> str:
    """
    Converts a snake_case string to camelCase.
    """
    parts = s.split('_')
    return parts[0] + ''.join(word.capitalize() for word in parts[1:])
class Model(BaseModel):
    pass


class APIKey(Model):
    api_key: str


class OktaUserProfile(Model):
    country: str = None
    lastName: str = None
    msftAlias: str = None
    manager: str = None
    costCenter: str = None
    secondEmail: str = None
    managerId: str = None
    costCenterHierarchy: str = None
    title: str = None
    login: str
    firstName: str = None
    employeeType: str = None
    githubDotcomId: str = None
    state: str = None
    email: str = None


class OktaUserCredentialProvider(Model):
    type: str = None
    name: str = None


class OktaUserCredentialInfo(Model):
    provider: OktaUserCredentialProvider = None


class OktaUser(Model):
    id: str
    status: str
    credentials: OktaUserCredentialInfo = None
    profile: OktaUserProfile = None
    created: datetime = None
    activated: datetime = None
    statusChanged: datetime = None
    lastLogin: datetime = None
    lastUpdated: datetime = None


class OktaFlatUser(OktaUser):
    lastName: str = None
    firstName: str = None
    manager: str = None
    githubDotcomId: str = None
    employeeType: str = None
    email: str = None

    @root_validator(pre=True)
    def flatten_profile(cls, values: GetterDict) -> GetterDict | dict[str, object]:
        if profile := values.get("profile"):
            profile = OktaUserProfile.validate(profile)
            return {
                "lastName": profile.lastName,
                "firstName": profile.firstName,
                "manager": profile.manager,
                "githubDotcomId": profile.githubDotcomId,
                "employeeType": profile.employeeType,
                "email": profile.email.lower(),
                "title": profile.title,
                "msftAlias": profile.msftAlias,
            } | dict(values)
        return {  # pragma: no cover
            "lastName": "",
            "firstName": "",
            "manager": "",
            "githubDotcomId": "",
            "employeeType": "",
            "email": "",
            "title": "",
        } | dict(values)


class OktaUserList(Model):
    __root__: List[OktaFlatUser]


class OktaGroupProfile(Model):
    name: str
    description: str


class OktaGroup(Model):
    id: str
    profile: OktaGroupProfile = None


class OktaGroupList(Model):
    __root__: List[OktaGroup]


class OktaApp(Model):
    id: str
    name: str = None
    label: str = None
    status: str = None
    created: str = None
    lastUpdated: str = None
    notes: str = None


class OktaAppsList(Model):
    __root__: List[OktaApp]


class OktaDeviceProfile(Model):
    displayName: str = None
    platform: str = None
    model: str = None
    serialNumber: str = None
    registered: bool = None
    secureHardwarePresent: bool = None
    diskEncryptionType: str = None


class OktaDeviceEmbeddedUser(Model):
    managementStatus: str = None
    user: OktaFlatUser = None


class OktaDeviceEmbedded(Model):
    users: List[OktaDeviceEmbeddedUser]


class OktaDevice(Model):
    id: str = None
    status: str = None
    profile: OktaDeviceProfile = None
    _embedded: OktaDeviceEmbedded = None


class OktaFlatDevice(OktaDevice):
    displayName: str = None
    platform: str = None
    model: str = None
    serialNumber: str = None
    registered: str = None
    secureHardwarePresent: str = None
    diskEncryptionType: str = None
    managementStatus: str = None
    userType: Optional[str] = None
    userStatus: Optional[str] = None
    userHandle: Optional[str] = None

    @root_validator(pre=True)
    def flatten(cls, values: GetterDict) -> GetterDict | dict[str, object]:
        if profile := values.get("profile"):
            profile = OktaDeviceProfile.validate(profile)
            device_dict = {
                "displayName": profile.displayName,
                "platform": profile.platform,
                "model": profile.model,
                "serialNumber": profile.serialNumber,
                "registered": profile.registered,
                "secureHardwarePresent": profile.secureHardwarePresent,
                "diskEncryptionType": profile.diskEncryptionType,
            }
            return device_dict | dict(values)
        return {  # pragma: no cover
            "displayName": "",
            "platform": "",
            "model": "",
            "serialNumber": "",
            "registered": "",
            "secureHardwarePresent": "",
            "diskEncryptionType": "",
        } | dict(values)

    @root_validator(pre=True)
    def flatten_embedded(cls, values: GetterDict) -> GetterDict | dict[str, object]:
        device_dict = {}
        if _embedded := values.get("_embedded"):
            embedded = OktaDeviceEmbedded.validate(_embedded)
            if embedded.users:
                device_dict["managementStatus"] = (
                    "MANAGED"
                    if any(u.managementStatus == "MANAGED" for u in embedded.users)
                    else embedded.users[0].managementStatus
                )
                device_dict["userType"] = next(
                    (
                        u.user.employeeType
                        for u in embedded.users
                        if u.managementStatus == "MANAGED"
                    ),
                    embedded.users[0].user.employeeType,
                )
                device_dict["userStatus"] = next(
                    (
                        u.user.status
                        for u in embedded.users
                        if u.managementStatus == "MANAGED"
                    ),
                    embedded.users[0].user.status,
                )
                device_dict["userHandle"] = next(
                    (
                        u.user.email
                        for u in embedded.users
                        if u.managementStatus == "MANAGED"
                    ),
                    embedded.users[0].user.email,
                )
        else:
            device_dict["managementStatus"] = ""
            device_dict["userType"] = ""
            device_dict["userStatus"] = ""
            device_dict["userHandle"] = ""
        return device_dict | dict(values)


class OktaDeviceList(Model):
    __root__: List[OktaFlatDevice]


class OomnitzaEndpoint(Model):
    equipment_id: str = None
    version: str = None
    creation_date: int = None
    change_date: int = None
    created_by: str = None
    changed_by: str = None
    location: str = None
    stockroom: str = None
    assigned_to: str = None
    barcode: str = None
    deleted: str = None
    asset_type: str = None
    serial_number: str = None
    department: str = None
    status: str = None
    device_name: str = None
    currently_logged_in_user: str = None
    loan_return_date: str = None
    last_casper_checkin: int = None
    loan_out_date: str = None
    refresh_eligible: str = None
    logged_in_chrome_user: str = None
    is_loaner: str = None
    retirement_status: str = None
    estimated_delivery_date: str = None
    repair_start_date: str = None
    retirement_date: str = None
    to_be_retired_status: str = None
    in_service_date: int = None
    assigned_to_date: int = None
    hold_start_date: str = None
    lost_stolen_date: str = None
    sold_to: str = None
    udid: str = None
    not_github_managed: str = None
    okta_device_certificate_id: str = None
    verified_correct: str = None
    last_api_assignment_update: str = None
    automated_asset_offboarding_completed: str = None
    automated_asset_offboarding_started: str = None
    assigned_to_endpoint_manager: str = None
    device_os_installation_uuid: str = None
    zendesk_remove_from_dep_complete: str = None
    wipe_device_confirm: str = None
    user_no_longer_active: Optional[str] = ""
    legal_hold: Optional[str] = "0"


class EndpointUnderInvestigation(Model):
    udid: Optional[str] = ""
    serial_number: Optional[str] = ""
    assigned_to: Optional[str] = ""
    changed_by: Optional[str] = ""
    status: Optional[str] = ""
    user_no_longer_active: Optional[str] = ""
    change_date: Optional[str] = ""

    class Config:
        validate_assignment = True

    @validator("udid", pre=True, always=True)
    def set_udid(cls, udid):
        return udid or "unknown"

    @validator("serial_number", pre=True, always=True)
    def set_serial_number(cls, serial_number):
        return serial_number or "unknown"

    @validator("assigned_to", pre=True, always=True)
    def set_assigned_to(cls, assigned_to):
        return assigned_to or "unknown"

    @validator("changed_by", pre=True, always=True)
    def set_changed_by(cls, changed_by):
        return changed_by or "unknown"

    @validator("status", pre=True, always=True)
    def set_status(cls, status):
        return status or "None Found"

    @validator("user_no_longer_active", pre=True, always=True)
    def set_user_no_longer_active(cls, user_no_longer_active):
        return user_no_longer_active or "unknown"


class EndpointInvestigationList(Model):
    __root__: List[EndpointUnderInvestigation]


class ReportMetricBody(Model):
    family: str
    category: str
    name: str
    value: int = None
    description: str = None


class BulkReportMetricResponse(Model):
    count: int


class PageParams(Model):
    offset: conint(ge=0) = 0
    limit: conint(ge=1, le=1000) = 1000


class PageResponse(Model):
    """Response schema for any paged API."""

    total: int = 0
    results: List[Any]

    class Config:
        orm_mode = True


class MetricsPageResponse(Model):
    """Response schema for any paged API."""

    total: int = 0
    results: List[Any]

    class Config:
        orm_mode = True


# we combine all enums into one type for type checking
CombinedProcessNameEnum = Union[
    TestTaskProcesses, RunOneOffCampaignsProcesses, RunTemplatedCampaignsProcesses
]

# useful to have all the values enumerated.
combined_process_values = [
    n for t in get_args(CombinedProcessNameEnum) for n in t._member_names_
]


class PlaceholderValues(Model):
    """Placeholder values for long running tasks opt flags.

    Subject to change or removal.
    """

    placeholder: Literal["option_one"]


class OptFlags(Model):
    """OptFlag values for long running tasks.

    Currently unimplemented, but default value is set to avoid
    allowing random submissions.
    """

    placeholder: PlaceholderValues


class LongRunningTaskConfig(Model):
    """Body for config to pass to enqueue_process endpoint."""

    # known process_names live in an Enum
    process_name: CombinedProcessNameEnum
    dry_run: Optional[bool] = False
    task_lock_timeout_seconds: Optional[int] = 60
    opt_flags: Optional[OptFlags] = OptFlags(
        placeholder=PlaceholderValues(placeholder="option_one")
    )


# For more API information: https://learn.microsoft.com/en-us/graph/api/intune-devices-manageddevice-list?view=graph-rest-1.0&tabs=http#response-1
class IntuneDeviceData(Model):
    id: str
    user_id: Optional[str] = None
    device_name: Optional[str] = None
    compliance_state: Optional[str] = None
    managed_device_owner_type: Optional[str] = None
    operating_system: Optional[str] = None
    os_version: Optional[str] = None
    model: Optional[str] = None  # Includes Virtual Machine
    manufacturer: Optional[str] = None
    serial_number: Optional[str] = None
    udid: Optional[str] = None
    is_encrypted: Optional[bool] = None
    jail_broken: Optional[str] = None
    is_supervised: Optional[bool] = None
    enrollment_profile_name: Optional[str] = None

class Schema(BaseModel):
    class Config:
        alias_generator = camelize
        populate_by_name = True  # Pydantic will use the camelize function to automatically change field names to camelCase when it outputs data.
