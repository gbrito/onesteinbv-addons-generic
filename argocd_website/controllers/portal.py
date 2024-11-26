import logging

from odoo import _, http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager

_logger = logging.getLogger(__name__)

try:
    pass
except ImportError as err:
    _logger.debug(err)


class PortalController(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "app_count" in counters:
            app_count = request.env["argocd.application"].search_count([])
            values["app_count"] = app_count
        return values

    @http.route(
        ["/my/applications", "/my/applications/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_applications(self, page=1, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        searchbar_sortings = {
            "name": {"label": _("Name"), "order": "name desc"},
            "creation": {"label": _("Creation"), "order": "create_date desc"},
        }
        if not sortby:
            sortby = "name"
        order = searchbar_sortings[sortby]["order"]
        app_count = request.env["argocd.application"].search_count([])
        # pager
        pager = portal_pager(
            url="/my/applications",
            url_args={
                "sortby": sortby,
            },
            total=app_count,
            page=page,
            step=self._items_per_page,
        )
        apps = request.env["argocd.application"].search(
            [], order=order, limit=self._items_per_page, offset=pager["offset"]
        )
        values.update(
            {
                "apps": apps.sudo(),  # We don't have access to the invoice lines without this
                "page_name": "Applications",
                "pager": pager,
                "default_url": "/my/applications",
                "searchbar_sortings": searchbar_sortings,
                "sortby": sortby,
            }
        )
        return request.render("argocd_website.portal_my_applications", values)

    @http.route(
        ["/my/applications/<int:app_id>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_application_detail(self, app_id, **kw):
        try:
            app_sudo = self._document_check_access("argocd.application", app_id)
        except (AccessError, MissingError):
            return request.redirect("/my/applications")
        values = {
            "page_name": "Applications",
            "app": app_sudo,
            "message": kw.get("message"),
        }
        return request.render("argocd_website.portal_application_page", values)

    @http.route(
        ["/my/applications/<int:app_id>/domain-names"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_application_domain_names(self, app_id, **kw):
        try:
            app_sudo = self._document_check_access("argocd.application", app_id)
        except (AccessError, MissingError):
            return request.redirect("/my/applications")
        domains = app_sudo.domain_ids.filtered(lambda d: d.url)
        values = {
            "page_name": "Applications",
            "app": app_sudo,
            "domains": domains,
            "defaults": {d.id: d.name for d in domains},
        }

        if request.httprequest.method == "POST":
            message = "success"

            for domain in domains:
                # Set new defaults in case DNS check fails we don't want to reenter the domain again
                values["defaults"][domain.id] = kw.get(str(domain.id))

                # Check DNS
                # try:
                #     if not app_sudo.dns_cname_check(
                #         custom_domains[key]["value"], custom_domains[key].get("tag_id")
                #     ):  # Can still return False if inherited
                #         message = "error"
                # except (DNSException, ValidationError):
                #     message = "error"
            values["message"] = message

            if message == "error":
                return request.render(
                    "argocd_website.portal_application_domain_page", values
                )

            # Update and create new values
            # new_values = []
            # for key in custom_domains:
            #     existing_value = app_sudo.value_ids.filtered(lambda kp: kp.key == key)
            #     value = custom_domains[key]["value"]
            #     if existing_value:
            #         existing_value.value = value
            #     else:
            #         new_values.append({"key": key, "value": value})
            # app_sudo.value_ids = [Command.create(val) for val in new_values]
            return request.redirect("/my/applications")
        return request.render(
            "argocd_website.portal_application_domain_names_page", values
        )
