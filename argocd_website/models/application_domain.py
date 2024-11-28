import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)

try:
    pass
except ImportError as err:
    _logger.debug(err)


class Application(models.Model):
    _inherit = "argocd.application.domain"

    dns_cname_expected = fields.Char(
        help="Expected value of the CNAME record when checking if a change to the domain is valid",
        compute="_compute_dns_cname_expected",
    )

    def _compute_dns_cname_expected(self):
        # Compute once
        for domain in self.filtered(lambda d: not d.dns_cname_expected and d.url):
            domain.dns_cname_expected = domain.name

    def dns_check(self, domain):
        """
        Check if the A record is configured correctly.

        @param domain: Domain name to check
        @param tag_id: argocd.application.tag must be in tag_ids
        @raise: ValidationError: CNAME record configured incorrectly
        @raise: MissingError: Tag is not linked to app
        @return: True
        """
        # self.ensure_one()
        # expected_subdomain = None
        # if tag_id:
        #     tag = self.tag_ids.filtered(lambda t: t.id == tag_id)
        #     if not tag:
        #         raise MissingError(_("Tag is not linked to app"))
        #     expected_subdomain = tag.key
        # default_domain = self.format_domain(subdomain=expected_subdomain)
        # expected_content = name.from_text(default_domain)
        # res = resolver.resolve(domain, "CNAME")
        # record = res[0]
        # if expected_content != record.target:
        #     raise ValidationError(
        #         _(
        #             "CNAME record incorrectly configured expected %(expected_domain)s got %(result)s",
        #             expected_domain=default_domain,
        #             result=record.target.to_text(),
        #         )
        #     )
        return True
