import httpx
from typing import Any, List

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.reactive import reactive
from textual.widgets import Button, Static

from agentfile.app.components.types import ButtonType


class ServiceButton(Button):
    type: ButtonType = ButtonType.SERVICE


class ServicesList(Static):
    services = reactive([])

    def __init__(self, control_plane_url: str, **kwargs: Any):
        self.control_plane_url = control_plane_url
        super().__init__(**kwargs)

        self.refresh_services()

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="services-scroll"):
            for service in self.services:
                yield ServiceButton(service)

    def on_mount(self) -> None:
        self.set_interval(5, self.refresh_services)

    def refresh_services(self) -> None:
        with httpx.Client() as client:
            response = client.get(f"{self.control_plane_url}/services")
            services_dict = response.json()

        new_services = []
        for service_name in services_dict:
            new_services.append(service_name)

        self.services = [*new_services]

    def watch_services(self, new_services: List[str]) -> None:
        try:
            services_scroll = self.query_one("#services-scroll")
            services_scroll.remove_children()
            for service in new_services:
                services_scroll.mount(ServiceButton(service))
        except Exception:
            pass