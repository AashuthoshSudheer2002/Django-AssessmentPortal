from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import *
from .forms import *

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['title']

@admin.register(Criteria)
class CriteriaAdmin(admin.ModelAdmin):
    list_display = ['criteria_title','criteria_section']
    list_filter = ['criteria_section']

@admin.register(CriteriaWeight)
class CriteriaAdmin(admin.ModelAdmin):
    list_display = ['criteria','role','weight']
    list_filter = ['criteria__criteria_section']

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display=['title']

@admin.register(SectionWeight)
class SectionWeightAdmin(admin.ModelAdmin):
    form = SectionWeightForm
    list_display=['section','weight','role']
    list_filter = ['role']

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display=['name','email','role']

@admin.register(Evaluator)
class EvaluatorAdmin(admin.ModelAdmin):
    list_display=['user','candidate','section']
    form=EvaluatorForm

@admin.register(CandidateCriterionScore)
class CandidateScoreAdmin(admin.ModelAdmin):
    list_display = ['candidate','criterion','score','evaluator','is_evaluated']
    form = CandidateCriteriaForm