from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from workflows.models import State
from workflows.models import StateInheritanceBlock
from workflows.models import StatePermissionRelation
from workflows.models import StateObjectRelation
from workflows.models import Transition
from workflows.models import Workflow
from workflows.models import WorkflowObjectRelation
from workflows.models import WorkflowModelRelation
from workflows.models import WorkflowPermissionRelation


def retrieve_parent_workflow(request):
    #TODO: is there a better way ?
    # retrieve object_id from path_info
    try:
        # ex: u'/admin/paintdb/recipe/203421/'
        path_info = request.META['PATH_INFO']
        object_id = int(path_info.strip('/').split('/')[-1])
        workflow = Workflow.objects.get(pk=object_id)
    except:
        workflow = None
    return workflow


class StateAdminMixin(object):

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'transitions':
            workflow = retrieve_parent_workflow(request)
            if workflow:
                queryset = workflow.transitions
            else:
                queryset = Transition.objects.none()
            kwargs["queryset"] = queryset
        return super(StateAdminMixin, self).formfield_for_manytomany(db_field, request, **kwargs)


class StateAdmin(StateAdminMixin, admin.ModelAdmin):
    list_display = ['__unicode__', 'transition_listing', 'workflow', ]
    list_filter = ['workflow', ]
    filter_horizontal = ['transitions', ]

    def transition_listing(self, obj):
        try:
            html = '<br />'.join([item.__unicode__() for item in obj.transitions.all()])
        except:
            html = ''
        return html
    transition_listing.short_description = _(u'transitions')
    transition_listing.allow_tags = True


class StateInline(StateAdminMixin, admin.TabularInline):
    model = State
    filter_horizontal = ['transitions', ]
    extra = 0


class WorkflowAdmin(admin.ModelAdmin):
    inlines = [
        StateInline,
    ]
    list_display = ['name', 'initial_state', 'state_listing', 'transition_listing', ]

    def state_listing(self, obj):
        try:
            html = '<br />'.join([item.__unicode__() for item in obj.states.all()])
        except:
            html = ''
        return html
    state_listing.short_description = _(u'states')
    state_listing.allow_tags = True

    def transition_listing(self, obj):
        try:
            html = '<br />'.join([item.__unicode__() for item in obj.transitions.all()])
        except:
            html = ''
        return html
    transition_listing.short_description = _(u'transitions')
    transition_listing.allow_tags = True

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "initial_state":
            workflow = retrieve_parent_workflow(request)
            if workflow:
                queryset = workflow.states.all()
            else:
                queryset = State.objects.none()
            kwargs["queryset"] = queryset
        return super(WorkflowAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class TransitionAdminMixin(object):

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'destination':
            workflow = retrieve_parent_workflow(request)
            if workflow:
                queryset = workflow.states
            else:
                queryset = Transition.objects.none()
            kwargs["queryset"] = queryset
        return super(TransitionAdminMixin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class TransitionAdmin(TransitionAdminMixin, admin.ModelAdmin):
    list_display = ['__unicode__', 'destination', 'permission_listing', 'workflow', ]
    list_filter = ['workflow', ]

    def permission_listing(self, obj):
        try:
            html = '<br />'.join([item.__unicode__() for item in obj.permissions.all()])
        except:
            html = ''
        return html
    permission_listing.short_description = _(u'permissions')
    permission_listing.allow_tags = True

admin.site.register(Workflow, WorkflowAdmin)
admin.site.register(State, StateAdmin)
admin.site.register(StateInheritanceBlock)
admin.site.register(StateObjectRelation)
admin.site.register(StatePermissionRelation)
admin.site.register(Transition, TransitionAdmin)
admin.site.register(WorkflowObjectRelation)
admin.site.register(WorkflowModelRelation)
admin.site.register(WorkflowPermissionRelation)
