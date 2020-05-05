# encoding: utf-8


from apispec_drf.decorators import apispec_list_operation, apispec_post_operation, apispec_get_operation, \
    apispec_delete_operation, apispec_put_operation
from backpack.models import BackpackBadgeShare
from backpack.serializers_v1 import LocalBadgeInstanceUploadSerializerV1
from entity.api import BaseEntityListView, BaseEntityDetailView
from issuer.models import BadgeInstance
from issuer.permissions import RecipientIdentifiersMatch, BadgrOAuthTokenHasScope
from issuer.public_api import ImagePropertyDetailView
from mainsite.exceptions import BadgrApiException400
from mainsite.permissions import AuthenticatedWithVerifiedEmail
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_302_FOUND, HTTP_204_NO_CONTENT


class BackpackAssertionList(BaseEntityListView):
    model = BadgeInstance
    v1_serializer_class = LocalBadgeInstanceUploadSerializerV1
    permission_classes = (AuthenticatedWithVerifiedEmail, RecipientIdentifiersMatch, BadgrOAuthTokenHasScope)
    http_method_names = ('get', 'post')
    valid_scopes = {
        'get': ['r:backpack', 'rw:backpack'],
        'post': ['rw:backpack'],
    }

    def get_objects(self, request, **kwargs):
        return [a for a in self.request.user.cached_badgeinstances() if (not a.revoked)
                                and a.acceptance != BadgeInstance.ACCEPTANCE_REJECTED
                                and not a.signing_in_progress]

    @apispec_list_operation('Assertion',
        summary="Get a list of Assertions in authenticated user's backpack ",
        tags=['Backpack']
    )
    def get(self, request, **kwargs):
        mykwargs = kwargs.copy()
        mykwargs['expands'] = []
        expands = request.GET.getlist('expand', [])

        if 'badgeclass' in expands:
            mykwargs['expands'].append('badgeclass')
        if 'issuer' in expands:
            mykwargs['expands'].append('issuer')

        return super(BackpackAssertionList, self).get(request, **mykwargs)

    @apispec_post_operation('Assertion',
        summary="Upload a new Assertion to the backpack",
        tags=['Backpack']
    )
    def post(self, request, **kwargs):
        if kwargs.get('version', 'v1') == 'v1':
            return super(BackpackAssertionList, self).post(request, **kwargs)

        raise NotImplementedError("use BackpackImportBadge.post instead")

    def get_context_data(self, **kwargs):
        context = super(BackpackAssertionList, self).get_context_data(**kwargs)
        context['format'] = self.request.query_params.get('json_format', 'v1')  # for /v1/earner/badges compat
        return context


class BackpackAssertionDetail(BaseEntityDetailView):
    model = BadgeInstance
    v1_serializer_class = LocalBadgeInstanceUploadSerializerV1
    permission_classes = (AuthenticatedWithVerifiedEmail, RecipientIdentifiersMatch, BadgrOAuthTokenHasScope)
    http_method_names = ('get', 'delete', 'put')
    valid_scopes = {
        'get': ['r:backpack', 'rw:backpack'],
        'put': ['rw:backpack'],
        'delete': ['rw:backpack'],
    }

    def get_context_data(self, **kwargs):
        context = super(BackpackAssertionDetail, self).get_context_data(**kwargs)
        context['format'] = self.request.query_params.get('json_format', 'v1')  # for /v1/earner/badges compat
        return context

    @apispec_get_operation('Assertion',
        summary="Get detail on an Assertion in the user's Backpack",
        tags=['Backpack']
    )
    def get(self, request, **kwargs):
        mykwargs = kwargs.copy()
        mykwargs['expands'] = []
        expands = request.GET.getlist('expand', [])

        if 'badgeclass' in expands:
            mykwargs['expands'].append('badgeclass')
        if 'issuer' in expands:
            mykwargs['expands'].append('issuer')

        return super(BackpackAssertionDetail, self).get(request, **mykwargs)

    @apispec_delete_operation('Assertion',
        summary='Remove an assertion from the backpack',
        tags=['Backpack']
    )
    def delete(self, request, **kwargs):
        obj = self.get_object(request, **kwargs)
        obj.acceptance = BadgeInstance.ACCEPTANCE_REJECTED
        obj.public = False
        obj.save()
        return Response(status=HTTP_204_NO_CONTENT)

    @apispec_put_operation('Assertion',
        summary="Update acceptance of an Assertion in the user's Backpack",
        tags=['Backpack']
    )
    def put(self, request, **kwargs):
        fields_whitelist = ('acceptance', 'public')
        data = {k: v for k, v in list(request.data.items()) if k in fields_whitelist}
        return super(BackpackAssertionDetail, self).put(request, data=data, **kwargs)


class BackpackAssertionDetailImage(ImagePropertyDetailView, BadgrOAuthTokenHasScope):
    model = BadgeInstance
    prop = 'image'
    valid_scopes = ['r:backpack', 'rw:backpack']


class ShareBackpackAssertion(BaseEntityDetailView):
    model = BadgeInstance
    permission_classes = (permissions.AllowAny,)  # this is AllowAny to support tracking sharing links in emails
    http_method_names = ('get',)

    def get(self, request, **kwargs):
        """
        Share a single badge to a support share provider
        ---
        parameters:
            - name: provider
              description: The identifier of the provider to use. Supports 'facebook', 'linkedin'
              required: true
              type: string
              paramType: query
        """
        # from recipient.api import _scrub_boolean
        redirect = request.query_params.get('redirect', "1")

        provider = request.query_params.get('provider')
        if not provider:
            fields = {'error_message': "Unspecified share provider", 'error_code': 701}
            raise BadgrApiException400(fields)
        provider = provider.lower()

        source = request.query_params.get('source', 'unknown')

        badge = self.get_object(request, **kwargs)
        if not badge:
            return Response(status=HTTP_404_NOT_FOUND)

        share = BackpackBadgeShare(provider=provider, badgeinstance=badge, source=source)
        share_url = share.get_share_url(provider)
        if not share_url:
            fields = {'error_message': "Invalid share provider", 'error_code': 702}
            raise BadgrApiException400(fields)

        share.save()

        if redirect:
            headers = {'Location': share_url}
            return Response(status=HTTP_302_FOUND, headers=headers)
        else:
            return Response({'url': share_url})
