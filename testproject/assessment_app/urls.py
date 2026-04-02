from django.urls import path
from .views import *


urlpatterns =[
    path('',home,name='home'),
    path('candidatedetail/<int:pk>/',CandidateDetailView.as_view(),name='candidate-detail'),
    path('candidatelist/',CandidateListView.as_view(),name='candidate-list'),
    path('candidateregister/',CandidateRegisterView.as_view(),name='candidate-register'),
    path('candidatescore/',CandidateScoreListView.as_view(),name='candidate-scores'),
    path('criteriascore/',CriteriaScoreView.as_view(),name='criteriascore'),
    path('criteriaregister/',CriteriaRegisterView.as_view(),name='criteriaregister'),
    path('sectionregister/',SectionRegisterView.as_view(),name='sectionregister'),
    path('ajax/load-criteria/', load_criteria, name='ajax_load_criteria'),
    path('ajax/get-evaluators/', get_evaluators, name='ajax_get_evaluators'),
    # path('fullscore/<int:candidate_id>/',submit_scores,name='fullscore'),
    path('createroleform/',createroleform,name='createrole'),
    path('trial/',evaluator_candidates_view,name='trial'),
    path('evalsec/<int:candidate_id>/',submit_eval_scores,name='evalscorer'),
    path('evaluatorassign/',assign_evaluators,name='assign-evaluator'),
    path('ajax/get_sections/', get_available_sections, name='get_sections'),
    path('login/',CustomLoginView.as_view(),name='login'),
    path('logout/',CustomLogoutView.as_view(),name='logout'),

]