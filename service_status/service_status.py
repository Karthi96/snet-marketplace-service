import re
import json
from datetime import datetime as dt
from datetime import timedelta
from common.utils import Utils
from service_status.config import REGION_NAME, NOTIFICATION_ARN, SLACK_HOOK
from common.boto_utils import BotoUtils
from common.utils import Utils
from common.logger import get_logger
from service_status.constant import MAXIMUM_INTERVAL_IN_HOUR, MINIMUM_INTERVAL_IN_HOUR
from service_status.constant import SRVC_STATUS_GRPC_TIMEOUT, LIMIT
from grpc_health.v1 import health_pb2 as heartb_pb2
from grpc_health.v1 import health_pb2_grpc as heartb_pb2_grpc
import grpc

logger = get_logger(__name__)
boto_util = BotoUtils(region_name=REGION_NAME)
util = Utils()


class ServiceStatus:
    def __init__(self, repo, net_id):
        self.repo = repo
        self.route = "/encoding"
        self.rex_for_pb_ip = "^(http://)*(https://)*127.0.0.1|^(http://)*(https://)*localhost|^(http://)*(https://)*192.|^(http://)*(https://)*172.|^(http://)*(https://)*10."
        self.obj_util = Utils()
        self.net_id = net_id

    def _get_service_status(self, url, secure=True):
        try:
            if secure:
                channel = grpc.secure_channel(
                    url, grpc.ssl_channel_credentials())
            else:
                channel = grpc.insecure_channel(url)

            stub = heartb_pb2_grpc.HealthStub(channel)
            response = stub.Check(heartb_pb2.HealthCheckRequest(
                service=""), timeout=SRVC_STATUS_GRPC_TIMEOUT)
            if response is not None and response.status == 1:
                logger.info(response.status)
                return 1
            return 0
        except Exception as e:
            logger.info(f"error in making grpc call::url: {url}, |error: {e}")
            return 0

    def _ping_url(self, url):
        search_count = re.subn(self.rex_for_pb_ip, "", url)[1]
        if search_count == 0:
            secure = True
            if url[:4].lower() == "http" and url[:5].lower() != "https":
                secure = False
            url = self.obj_util.remove_http_https_prefix(url=url)
            return self._get_service_status(url=url, secure=secure)
        return 0

    def _get_service_endpoint_data(self):
        query = "SELECT row_id, org_id, service_id, endpoint, is_available, status_change_count FROM service_endpoint WHERE " \
                "next_check_timestamp < CURRENT_TIMESTAMP AND endpoint not regexp %s ORDER BY last_check_timestamp ASC " \
                "LIMIT %s"
        result = self.repo.execute(query, [self.rex_for_pb_ip, LIMIT])
        if result is None or result == []:
            raise Exception("Unable to find services.")

    def _update_service_endpoint(self, status, next_check_timestamp, status_change_count, row_id):
        update_query = "UPDATE service_endpoint SET is_available = %s, last_check_timestamp = current_timestamp, " \
                       "next_check_timestamp = %s, status_change_count = %s WHERE row_id = %s "
        response = self.repo.execute(update_query, [status, next_check_timestamp, status_change_count, row_id])
        return response

    def update_service_status(self):
        service_endpoint_data = self._get_service_endpoint_data()
        for record in service_endpoint_data:
            status = self._ping_url(record["endpoint"])
            status_change_count = self._calculate_status_change_count(
                current_status=status, old_status=record["is_available"],
                old_status_change_count=record["status_change_count"])
            next_check_timestamp = self._calculate_next_check_timestamp(status_change_count=status_change_count)
            query_data = self._update_service_endpoint(status=status, next_check_timestamp=next_check_timestamp,
                                                       status_change_count=status_change_count, row_id=record["row_id"])
            rows_updated = 0
            if status == 0:
                org_id = record["org_id"]
                service_id = record["service_id"]
                self._send_notification(org_id=org_id, service_id=service_id, recipient=None)
            rows_updated = rows_updated + query_data[0]
        logger.info(f"no of rows updated: {rows_updated}")

    def _calculate_status_change_count(self, current_status, old_status, old_status_change_count):
        if current_status == old_status == 0:
            return old_status_change_count + 1
        return 1

    def _calculate_next_check_timestamp(self, status_change_count):
        time_delta_in_hours = MINIMUM_INTERVAL_IN_HOUR * (2 ** (status_change_count - 1))
        if time_delta_in_hours > MAXIMUM_INTERVAL_IN_HOUR:
            time_delta_in_hours = MAXIMUM_INTERVAL_IN_HOUR
        next_check_timestamp = dt.utcnow() + timedelta(hours=time_delta_in_hours)
        return next_check_timestamp

    def _send_notification(self, org_id, service_id, recipient=None):
        slack_message = self._get_slack_message(org_id=org_id, service_id=service_id)
        util.report_slack(type=0, slack_msg=slack_message, SLACK_HOOK=SLACK_HOOK)
        if recipient is None:
            pass
        else:
            self._send_email_notification(org_id=org_id, service_id=service_id)

    def _get_email_notification_payload(self, org_id, service_id, recipient):
        send_notification_payload = {
            "message": f"<html><head></head><body><div><p>Hello,</p><p>Your service {service_id} under organization "
                       f"{org_id} is down.</p><br /> <br /><p><em>Please do not reply to the email for any enquiries "
                       f"for any queries please email at cs-marketplace@singularitynet.io.</em></p><p>Warmest regards,"
                       f"<br />SingularityNET Marketplace Team</p></div></body></html>",
            "subject": f"Your service {service_id} is down.",
            "notification_type": "support",
            "recipient": recipient}

    def _get_slack_message(self, org_id, service_id):
        slack_message = f"```Alert!\n\nService {service_id} under organization {org_id} is down.\n\nFor any queries " \
                        f"please email at tech-support@singularitynet.io. \n\nWarmest regards,\nSingularityNET " \
                        f"Marketplace Team```"
        return slack_message

    def _send_email_notification(self, org_id, service_id, recipient):
        send_notification_payload = {
            "message": f"<html><head></head><body><div><p>Hello,</p><p>Your service {service_id} under organization "
                       f"{org_id} is down.</p><br /> <br /><p><em>Please do not reply to the email for any enquiries "
                       f"for any queries please email at cs-marketplace@singularitynet.io.</em></p><p>Warmest regards,"
                       f"<br />SingularityNET Marketplace Team</p></div></body></html>",
            "subject": f"Your service {service_id} is down.",
            "notification_type": "support",
            "recipient": recipient}
        boto_util.invoke_lambda(lambda_function_arn=NOTIFICATION_ARN, invocation_type="RequestResponse",
                                payload=json.dumps(send_notification_payload))

    def get_service_provider_email(self, org_id, service_id):
        pass