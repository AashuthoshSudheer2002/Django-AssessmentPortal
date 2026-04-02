from django.shortcuts import render, get_object_or_404,redirect
from .forms import *
from .models import *
from django.views.generic import *
from django.urls import reverse_lazy
from django.forms import modelformset_factory,ModelForm,Form,IntegerField,HiddenInput
from django.db.models import Sum,Q,Exists,OuterRef
from collections import defaultdict
from django.http import JsonResponse
from django.db import transaction
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.contrib.auth.views import LoginView, LogoutView



# Create your views here.
def home(request):
    return render(request,'home.html')

class CustomLoginView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('home')

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')

def load_criteria(request):
    candidate_id = request.GET.get('candidate_id')
    data = []

    if candidate_id:
        try:
            candidate = Candidate.objects.select_related('role').get(id=candidate_id)
            sections = Section.objects.filter()
            S = Section.objects.filter(id__in=SectionWeight.objects.filter(role=candidate.role).values_list('section_id', flat=True))
            criteria = Criteria.objects.filter(criteria_section__in=S)
            data = [{'id': c.id, 'title': c.criteria_title} for c in criteria]
        except Candidate.DoesNotExist:
            pass

    return JsonResponse(data, safe=False)

def get_evaluators(request):
    candidate_id = request.GET.get('candidate_id')
    evaluators = []
    if candidate_id:
        evaluators_qs = Evaluator.objects.filter(candidate_id=candidate_id)
        evaluators = [{'id': ev.id, 'name': ev.user.username} for ev in evaluators_qs]

    return JsonResponse({'evaluators': evaluators})





class CandidateDetailView(DetailView):
    model = Candidate
    template_name = 'candidate/detail.html'
    context_object_name = 'object'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        candidate = self.get_object()

        # Fetch scores grouped by section
        scores = (
            CandidateCriterionScore.objects
            .filter(candidate=candidate)
            .select_related('criterion__criteria', 'criterion__criteria__criteria_section')
            .order_by('criterion__criteria__criteria_section__title')
            .values(
                'criterion__criteria__criteria_section__title',
                'criterion__criteria__criteria_title',
                'score'
            )
        )

        # Group by section
        grouped_scores = {}
        for s in scores:
            section = s['criterion__criteria__criteria_section__title']
            grouped_scores.setdefault(section, []).append({
                'criterion_title': s['criterion__criteria__criteria_title'],
                'score': s['score']
            })

        context['grouped_scores'] = grouped_scores
        return context
    



class CandidateListView(ListView):
    queryset = Candidate.objects.all()
    template_name = 'candidate/list.html'
    context_object_name = 'candidates'



class CandidateRegisterView(CreateView):
    form_class = CandidateRegisterForm
    template_name = 'candidate/register.html'
    success_url = reverse_lazy('home')

class CriteriaRegisterView(CreateView):
    form_class = CriteriaForm
    template_name = 'criteria/register.html'
    success_url = reverse_lazy('home')

class SectionRegisterView(CreateView):
    form_class = SectionWeightForm
    template_name = 'section/register.html'
    success_url = reverse_lazy('home')


class CriteriaScoreView(CreateView):
    form_class = CandidateCriteriaForm
    template_name = 'candidate/score.html'
    success_url = reverse_lazy('home')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        candidate_id = self.request.GET.get('candidate')
        if candidate_id:
            form.fields['evaluator'].queryset = Evaluator.objects.filter(candidate_id=candidate_id)
        return form

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        candidate_id = self.request.GET.get('candidate')
        if candidate_id:
            try:
                candidate = get_object_or_404(Candidate, pk=int(candidate_id))
                kwargs.update({'initial': {'candidate': candidate}})
                if self.request.method in ('POST', 'PUT'):
                    kwargs['data'] = self.request.POST
            except (ValueError, Candidate.DoesNotExist):
                pass

        return kwargs

class CandidateScoreListView(ListView):
    model = Candidate
    template_name = 'candidatescores.html'
    context_object_name = 'candidates'

    def get_queryset(self):
        return Candidate.objects.select_related('role')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        candidates = context['candidates']
        candidates_by_role = defaultdict(list)
        #showing_top = self.request.GET.get('top') == 'true'

        for candidate in candidates:
            # Annotate each criterion with weighted score
            weighted_scores = CandidateCriterionScore.objects.filter(candidate=candidate).annotate(
                weighted_score=ExpressionWrapper(
                    F('score') * (F('criterion__weight') / 100.0),
                    output_field=FloatField()
                )
            )

            # Sum scores by section
            section_scores = weighted_scores.values('criterion__criteria__criteria_section').annotate(
                total_weighted_score=Sum('weighted_score')
            )

            weighted_total = 0
            for item in section_scores:
                section_id = item['criterion__criteria__criteria_section']
                total_weighted_score = item['total_weighted_score'] or 0

                try:
                    section = Section.objects.get(id=section_id)
                    weight_obj = SectionWeight.objects.get(section=section, role=candidate.role)
                    weight = weight_obj.weight
                except (Section.DoesNotExist, SectionWeight.DoesNotExist):
                    weight = 0

                weighted_total += (total_weighted_score * weight) / 100.0

            score_rounded = round(weighted_total, 2)
            candidates_by_role[candidate.role].append({
                'candidate': candidate,
                'total_score': score_rounded,
                'percentage': round((score_rounded / 10) * 100,2),
            })
        # Sort, rank, and optionally filter top scorers per role
        for role, cand_list in candidates_by_role.items():
            cand_list.sort(key=lambda x: x['total_score'], reverse=True)
            for idx, entry in enumerate(cand_list, start=1):
                entry['rank'] = idx

        show_top = self.request.GET.get('top') == 'true'
        if show_top:
            
            for role, cand_list in candidates_by_role.items():
                if not cand_list:
                    continue
                top_score = cand_list[0]['total_score']
                top_scorers = [c for c in cand_list if c['total_score'] == top_score]
                candidates_by_role[role] = top_scorers

        context['candidates_by_role'] = dict(candidates_by_role)
        context['showing_top'] = show_top
        return context
            



@login_required
def evaluator_candidates_view(request):
    candidate_ids = Evaluator.objects.filter(user=request.user).values_list('candidate_id', flat=True)

    # Subquery to check if there are any unevaluated scores for each candidate
    unevaluated_exists = CandidateCriterionScore.objects.filter(
        candidate_id=OuterRef('pk'),
        evaluator__user=request.user,
        is_evaluated=False
    )

    # Annotate each candidate with is_fully_evaluated: True/False
    candidates = Candidate.objects.filter(id__in=candidate_ids).annotate(
        is_fully_evaluated=~Exists(unevaluated_exists)
    )

    return render(request, 'trial.html', {'candidates': candidates})




@login_required
def submit_eval_scores(request, candidate_id):
    candidate = get_object_or_404(Candidate, id=candidate_id)

    section_ids = SectionWeight.objects.filter(role=candidate.role).values_list('section_id', flat=True)
    evaluator_sections = Evaluator.objects.filter(user=request.user, candidate=candidate).values_list('section', flat=True)

    criteria_weights = CriteriaWeight.objects.filter(
        role=candidate.role,
        criteria__criteria_section__in=evaluator_sections
    ).select_related('criteria')

    criterion_section_map = {
        "criteria": [
            {"id": cw.id, "name": cw.criteria.criteria_title}
            for cw in criteria_weights
        ]
    }

    ScoreFormSet = modelformset_factory(
        CandidateCriterionScore,
        form=CandidateCriterionScoreForm,
        extra=max(criteria_weights.count(), 1),
        can_delete=False
    )

    if request.method == 'POST':
        formset = ScoreFormSet(request.POST, queryset=CandidateCriterionScore.objects.none(), form_kwargs={'candidate': candidate})
        if formset.is_valid():
            for form in formset:
                if form.cleaned_data:
                    obj = form.save(commit=False)
                    obj.candidate = candidate
                    obj.is_evaluated = True

                    # Get section from nested relations: CriteriaWeight → Criteria → Section
                    section = obj.criterion.criteria.criteria_section
                    obj.evaluator = Evaluator.objects.get(user=request.user, candidate=candidate, section=section)

                    CandidateCriterionScore.objects.update_or_create(
                        candidate=candidate,
                        criterion=obj.criterion,
                        evaluator=obj.evaluator,
                        defaults={'score': obj.score, 'is_evaluated': True}
                    )
            return redirect('home')
    else:
        formset = ScoreFormSet(queryset=CandidateCriterionScore.objects.none(), form_kwargs={'candidate': candidate})

    return render(request, 'criteria/submitscore.html', {
        'formset': formset,
        'candidate': candidate,
        'criterion_section_map': criterion_section_map,
    })




def assign_evaluators(request):
    candidate_form = CandidateSelectionForm(request.POST or None)
    section_forms = []

    selected_candidate = None

    if request.method == "POST":
        candidate_id = request.POST.get('candidate')
        if candidate_id:
            try:
                selected_candidate = Candidate.objects.get(id=candidate_id)
            except Candidate.DoesNotExist:
                selected_candidate = None

        # Build forms for sections
        sections = SectionWeight.objects.filter(role=selected_candidate.role).select_related('section') if selected_candidate else []

        # Create section forms from POST data
        for i, sw in enumerate(sections):
            form = SectionEvaluatorForm(request.POST, prefix=f'section_{i}')
            section_forms.append(form)

        if candidate_form.is_valid() and all(f.is_valid() for f in section_forms):
            # Save evaluator assignments
            for form in section_forms:
                section_id = form.cleaned_data['section_id']
                evaluator = form.cleaned_data['evaluator']
                if evaluator:
                    # Check if this assignment already exists
                    exists = Evaluator.objects.filter(candidate=selected_candidate, section_id=section_id, user=evaluator).exists()
                    if not exists:
                        Evaluator.objects.create(candidate=selected_candidate, section_id=section_id, user=evaluator)

            messages.success(request, "Evaluators assigned successfully.")
            return redirect('home')
        else:
            messages.error(request, "Please correct the errors below.")

    else:
        # GET request
        if candidate_form.is_valid() and candidate_form.cleaned_data.get('candidate'):
            selected_candidate = candidate_form.cleaned_data['candidate']

        if selected_candidate:
            sections = SectionWeight.objects.filter(role=selected_candidate.role).select_related('section')
            for i, sw in enumerate(sections):
                # Get evaluators already assigned for this section and candidate
                assigned_evaluators = Evaluator.objects.filter(candidate=selected_candidate, section=sw.section).values_list('user_id', flat=True)
                # Exclude assigned evaluators from queryset
                available_evaluators = User.objects.exclude(id__in=assigned_evaluators)
                
                form = SectionEvaluatorForm(prefix=f'section_{i}')
                form.fields['section_id'].initial = sw.section.id
                form.fields['section_title'].initial = sw.section.title
                form.fields['evaluator'].queryset = available_evaluators
                section_forms.append(form)

    context = {
        'candidate_form': candidate_form,
        'section_forms': section_forms,
        'selected_candidate': selected_candidate,
    }
    return render(request, 'Evaluator/evaluatorform.html', context)


def get_available_sections(request):
    candidate_id = request.GET.get('candidate_id')
    if not candidate_id:
        return JsonResponse({'error': 'No candidate id provided.'}, status=400)

    try:
        candidate = Candidate.objects.get(id=candidate_id)
    except Candidate.DoesNotExist:
        return JsonResponse({'error': 'Candidate not found.'}, status=404)

    sections = SectionWeight.objects.filter(role=candidate.role).select_related('section')
    section_forms_html = []

    for i, sw in enumerate(sections):
        assigned_evaluators = Evaluator.objects.filter(candidate=candidate, section=sw.section).values_list('user_id', flat=True)
        available_evaluators = User.objects.exclude(id__in=assigned_evaluators)

        form = SectionEvaluatorForm(prefix=f'section_{i}')
        form.fields['section_id'].initial = sw.section.id
        form.fields['section_title'].initial = sw.section.title
        form.fields['evaluator'].queryset = available_evaluators

        # Render each form to HTML and collect
        html = render_to_string('partial_section_evaluator_form.html', {'form': form})
        section_forms_html.append(html)
        print(section_forms_html)

    return JsonResponse({'section_forms_html': section_forms_html})

def createroleform(request):
    sections = list(Section.objects.values('id', 'title'))

    # Prepare a dictionary of criteria grouped by section
    criteria_by_section = {
        section.id: list(section.criteria.values('id', 'criteria_title','criteria_section'))
        for section in Section.objects.all()
    }

    if request.method == "POST":
        try:
            with transaction.atomic():
                role_title = request.POST.get('role_title')
                if not role_title:
                    raise ValueError("Role title is required.")

                role = Role.objects.create(title=role_title)

                for section in Section.objects.all():
                    section_id = str(section.id)
                    weight_str = request.POST.get(f'section_weight_{section_id}', '0')

                    try:
                        weight = int(weight_str)
                    except ValueError:
                        raise ValueError(f"Invalid weight for section {section.title}.")

                    # Save section weight for this role
                    SectionWeight.objects.create(role=role, section=section, weight=weight)

                    # Handle criteria weights for this section
                    for criteria in section.criteria.all():
                        crit_id = str(criteria.id)
                        c_weight_str = request.POST.get(f'criteria_weight_{section_id}_{crit_id}', '0')

                        try:
                            c_weight = int(c_weight_str)
                        except ValueError:
                            raise ValueError(
                                f"Invalid criteria weight for '{criteria.title}' in section '{section.title}'."
                            )

                        # Save CriteriaWeight
                        CriteriaWeight.objects.create(
                            role=role,
                            criteria=criteria,
                            weight=c_weight
                        )

            return redirect('home')

        except Exception as e:
            return render(request, 'Role/Create2.html', {
                'form': None,
                'sections': sections,
                'criteria_by_section': criteria_by_section,
                'error': str(e)
            })

    return render(request, 'Role/Create2.html', {
        'form': None,
        'sections': sections,
        'criteria_by_section': criteria_by_section
    })