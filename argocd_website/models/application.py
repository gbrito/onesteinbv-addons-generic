import logging

import requests

from odoo import fields, models

_logger = logging.getLogger(__name__)

try:
    pass
except ImportError as err:
    _logger.debug(err)


class Application(models.Model):
    _name = "argocd.application"
    _inherit = ["argocd.application", "portal.mixin"]

    deletion_token = fields.Char()
    deletion_token_expiration = fields.Datetime()

    def _compute_access_url(self):
        for record in self:
            record.access_url = "/my/applications/{}".format(record.id)

    def check_health(self):
        self.ensure_one()
        statuses = []
        urls = self.get_urls()
        for url in urls:
            try:
                response = requests.get(url[0])
                statuses.append(response.ok)
            except Exception:
                statuses.append(False)
        return statuses
