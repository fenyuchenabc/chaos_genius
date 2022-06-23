"""Utilities for sending slack alert messages."""
import logging
from typing import TYPE_CHECKING, Optional, Sequence

from slack_sdk.webhook.client import WebhookClient

import chaos_genius.alerts.anomaly_alerts as anomaly_alerts

if TYPE_CHECKING:
    from chaos_genius.controllers.digest_controller import AlertsReportData

from chaos_genius.alerts.alert_channel_creds import get_slack_creds
from chaos_genius.alerts.utils import webapp_url_prefix

logger = logging.getLogger(__name__)


def get_webhook_client() -> WebhookClient:
    """Initializes a Slack Webhook client."""
    url = get_slack_creds()
    return WebhookClient(url)


def anomaly_alert_slack(
    data: "anomaly_alerts.AlertsIndividualData",
) -> str:
    """Sends an anomaly alert on slack.

    Returns an empty string if successful or the error as a string if not.
    """
    # TODO: Fix this implementation to use AlertsIndividualData
    client = get_webhook_client()
    response = client.send(
        blocks=[
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": (
                        f"{data.alert_name} - {data.kpi_name} "
                        f"({data.date_formatted()}) "
                    ),
                    "emoji": True,
                },
            },
            {
                "type": "divider",
            },
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "Alert Message",
                    "emoji": True,
                },
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"{data.alert_message}\n"},
            },
            {
                "type": "divider",
            },
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "Anomalies",
                    "emoji": True,
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": _format_slack_anomalies(
                        data.top_overall_points,
                        kpi_name=data.kpi_name,
                        include_kpi_info=False,
                    ),
                },
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "View KPI"},
                        "url": data.kpi_link(),
                        "action_id": "kpi_link",
                        "style": "primary",
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Alerts Dashboard"},
                        "url": data.alert_dashboard_link(),
                        "action_id": "alert_dashboard",
                        "style": "primary",
                    },
                ],
            },
        ],
    )

    if response.body != "ok":
        return response.body

    return ""


def event_alert_slack(alert_name, alert_frequency, alert_message, alert_overview):
    client = get_webhook_client()
    if not client:
        raise Exception("Slack not configured properly.")
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"Alert: {alert_name}",
                "emoji": True,
            },
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"Alert Frequency : {alert_frequency}",
            },
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"Alert Message : {alert_message}",
            },
        },
    ]
    if alert_overview:
        blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Alert Overview : {alert_overview}",
                },
            }
        )
    response = client.send(text=f"Event Alert: {alert_name}", blocks=blocks)
    return response.body


def _format_slack_anomalies(
    top10: "Sequence[anomaly_alerts.AnomalyPointFormatted]",
    kpi_name: Optional[str] = None,
    include_kpi_info: bool = True,
) -> str:
    out = ""

    for point in top10:

        if include_kpi_info:
            kpi_name_link = (
                f"<{webapp_url_prefix()}#/dashboard/0/anomaly/{point.kpi_id}"
                + f"|{point.kpi_name}>"
            )
        else:
            kpi_name_link = f"{kpi_name}"

        if point.previous_value is None or point.y == point.previous_value:
            out += "- :black_circle_for_record: Anomalous behavior"
            if include_kpi_info:
                out += f" in *{kpi_name_link}* "
            else:
                out += " detected "
            if point.previous_value is None:
                out += f"- changed to *{point.y_readable}*"
                if point.is_hourly:
                    out += (
                        f" from {point.previous_point_time_only}"
                        + f" to {point.anomaly_time_only}"
                    )
            else:
                if point.is_hourly:
                    out += (
                        f"- with constant value *{point.y_readable}*"
                        + f" from {point.previous_point_time_only}"
                        + f" to {point.anomaly_time_only}"
                    )
                else:
                    out += f"- with same value *{point.y_readable}* as previous day"

        else:
            if point.y > point.previous_value:
                out += "- :arrow_up: Spike"
            elif point.y < point.previous_value:
                out += "- :arrow_down_small: Drop"
            if include_kpi_info:
                out += f" in *{kpi_name_link}* "
            else:
                out += " detected "
            out += f" -  changed to *{point.y_readable}*"
            if point.previous_value_readable is not None:
                out += (
                    f" from {point.previous_value_readable} "
                    + f"({point.formatted_change_percent})"
                )
            if point.is_hourly:
                out += (
                    f" from {point.previous_point_time_only}"
                    + f" to {point.anomaly_time_only}"
                )
        out += "\n"

    return out


def alert_digest_slack_formatted(data: "AlertsReportData") -> str:
    """Sends an anomaly digest on slack.

    Returns an empty string if successful or the error as a string if not.
    """
    client = get_webhook_client()
    if not client:
        raise Exception("Slack not configured properly.")

    response = client.send(
        blocks=[
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"Daily Alerts Report ({data.report_date_formatted()})",
                    "emoji": True,
                },
            },
            {
                "type": "divider",
            },
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "Top Anomalies",
                    "emoji": True,
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": _format_slack_anomalies(data.top_anomalies),
                },
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Alerts Dashboard"},
                        "url": data.alert_dashboard_link(),
                        "action_id": "alert_dashboard",
                        "style": "primary",
                    }
                ],
            },
        ]
    )

    if response.body != "ok":
        return response.body

    return ""


def alert_table_sender(client, table_data):
    response = client.send(text=table_data)
    return response.body


def trigger_overall_kpi_stats(
    alert_name, kpi_name, data_source_name, alert_body, stats
):
    client = get_webhook_client()
    if not client:
        raise Exception("Slack not configured properly.")
    response = client.send(
        text="fallback",
        blocks=[
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"Alert: {alert_name}",
                    "emoji": True,
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"This is the alert generated from KPI *{kpi_name}* and Data Source *{data_source_name}*.",
                },
            },
            {
                "type": "section",
                "text": {"type": "plain_text", "text": f"{alert_body}", "emoji": True},
            },
            {"type": "divider"},
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Sum:*\n{stats['current']['sum']} ({stats['past']['sum']})",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Mean:*\n{stats['current']['mean']} ({stats['past']['mean']})",
                    },
                ],
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Change from last week:*\n{stats['impact']['sum']}",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Change from last week:*\n{stats['impact']['mean']}",
                    },
                ],
            },
        ],
    )
    return True


def test():
    client = get_webhook_client()
    if not client:
        raise Exception("Slack not configured properly.")
    response = client.send(
        text="fallback",
        blocks=[
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "Anomaly Alert from Chaos Genius ",
                    "emoji": True,
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "plain_text",
                    "text": "There are some new anomaly found in some of the KPI.",
                    "emoji": True,
                },
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": '*KPI:*\nConversion Rate\n*Value:*\n10\n*When:*\nJuly 20\n*Comments:* "View Drill Down for more info!"',
                },
                "accessory": {
                    "type": "image",
                    "image_url": "https://user-images.githubusercontent.com/20757311/126447967-c9f09b9a-d917-4f3f-bc69-94c3318705fe.png",
                    "alt_text": "cute cat",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Click here to open the drilldowns in dashboard.",
                },
                "accessory": {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Dashboard", "emoji": True},
                    "value": "click_me_123",
                    "url": "https://chaosgenius.mayhemdata.com/#/dashboard",
                    "action_id": "button-action",
                },
            },
            {
                "type": "image",
                "title": {"type": "plain_text", "text": "Anomaly Found", "emoji": True},
                "image_url": "https://user-images.githubusercontent.com/20757311/126447329-a30e0b23-bf21-49c1-a029-d8de7691ef0f.png",
                "alt_text": "marg",
            },
        ],
    )
    print(response.body)
