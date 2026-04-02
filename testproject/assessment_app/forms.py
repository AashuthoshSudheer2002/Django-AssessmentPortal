from django import forms
from django.core.validators import MaxValueValidator
from .models import *
from django.db.models import *
from django.forms import modelformset_factory
class SectionWeightForm(forms.ModelForm):
    class Meta:
        model = SectionWeight
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = self.instance

        # Check if it's an existing instance (editing case) and both section and role are set
        if instance.pk and instance.section and instance.role:
            #section = instance.sections
            role = instance.role
            print(instance.pk,instance.section,instance.role)
            # Calculate the total weight for the section and role, excluding the current instance
            current_total = SectionWeight.objects.filter(role=role).exclude(pk=instance.pk).aggregate(
                total=Sum('weight')
            )['total'] or 0 
            print(current_total)
            remaining = 100 - current_total  
            print(remaining)
            self.fields['weight'].validators.append(MaxValueValidator(remaining))
            self.fields['weight'].help_text = f"Maximum allowed for this Section & Role: {remaining}%"
            self.remaining_weight = remaining
        else:
            # For new entries, the remaining weight will be 100 (until section and role are selected)
            self.remaining_weight = 100
            self.fields['weight'].help_text = "Remaining weight will be calculated once Section and Role are selected."

# class EvaluatorForm(forms.ModelForm):
#     class Meta:
#         model = Evaluator
#         fields = ['user', 'candidate', 'section']

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#         candidate_id = None
#         if 'candidate' in self.data:
#             candidate_id = self.data.get('candidate')
#         elif self.instance and self.instance.pk:
#             candidate_id = self.instance.candidate_id  # For editing existing instance

#         if candidate_id:
#             try:
#                 candidate = Candidate.objects.get(pk=candidate_id)
#                 role = candidate.role
#                 self.fields['section'].queryset = Section.objects.filter(
#                 id__in=SectionWeight.objects.filter(role=role).values_list('section_id', flat=True)
#             )
#             except Candidate.DoesNotExist:
#                 self.fields['section'].queryset = SectionWeight.objects.none()
#         else:
#             self.fields['section'].queryset = SectionWeight.objects.none()

from django import forms
from .models import Evaluator, Candidate, Section, SectionWeight

class EvaluatorForm(forms.ModelForm):
    class Meta:
        model = Evaluator
        fields = ['user', 'candidate', 'section']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Filter out candidates who already have been assigned evaluators for all sections
        assigned_candidate_ids = Evaluator.objects.values_list('candidate_id', flat=True).distinct()
        self.fields['candidate'].queryset = Candidate.objects.exclude(id__in=assigned_candidate_ids)

        self.fields['section'].queryset = Section.objects.none()
        self.fields['section'].widget.attrs['readonly'] = True
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super().clean()
        candidate = cleaned_data.get('candidate')
        section = cleaned_data.get('section')
        user = cleaned_data.get('user')

        if candidate and section and user:
            if Evaluator.objects.filter(candidate=candidate, section=section).exists():
                raise forms.ValidationError(
                    f"Section '{section}' already has an evaluator for candidate '{candidate}'."
                )
        return cleaned_data
class CriteriaForm(forms.ModelForm):
    class Meta:
        model = Criteria
        exclude = ['criteria_score']  

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        instance = self.instance
        print(instance)
        if instance and instance.pk and instance.criteria_section:
            section = instance.criteria_section

            current_total = Criteria.objects.filter(criteria_section=section).exclude(pk=instance.pk).aggregate(
                total=models.Sum('criteria_weight')
            )['total'] or 0

            remaining = 100 - current_total

            self.fields['criteria_weight'].validators.append(MaxValueValidator(remaining))
            self.fields['criteria_weight'].help_text = f"Maximum allowed for this section: {remaining}%"
        else:
            self.fields['criteria_weight'].help_text = "Set a section first to calculate remaining weight."

class CandidateRegisterForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(CandidateRegisterForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control',
                'placeholder': field.label  # required for floating labels
            })

class CandidateCriteriaForm(forms.ModelForm):
    class Meta:
        model = CandidateCriterionScore
        fields = ['candidate','criterion','score','evaluator']
        unique_together = ('candidate','criterion')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['evaluator'].queryset = Evaluator.objects.none()
        if 'candidate' in self.data:
            try:
                candidate_id = int(self.data.get('candidate'))
                candidate = Candidate.objects.get(id=candidate_id)
                self.fields['evaluator'].queryset = Evaluator.objects.filter(candidate=candidate)
            except (ValueError, Candidate.DoesNotExist):
                pass
        elif self.instance.pk:
            candidate = self.instance.candidate
            self.fields['evaluator'].queryset = Evaluator.objects.filter(candidate=candidate)    

class CandidateCriterionScoreForm(forms.ModelForm):
    class Meta:
        model = CandidateCriterionScore
        fields = ['criterion', 'score']

    def __init__(self, *args, **kwargs):
        candidate = kwargs.pop('candidate', None)
        super().__init__(*args, **kwargs)

        if candidate:
            self.fields['criterion'].queryset = CriteriaWeight.objects.filter(role=candidate.role)

        self.fields['criterion'].widget.attrs.update({'class': 'form-select'})
        self.fields['score'].widget = forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 10})




class CandidateSelectionForm(forms.Form):
    candidate = forms.ModelChoiceField(
        queryset=Candidate.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True,
        label='Candidate'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assigned_candidate_ids = Evaluator.objects.values_list('candidate_id', flat=True).distinct()
        self.fields['candidate'].queryset = Candidate.objects.exclude(id__in=assigned_candidate_ids)


class SectionEvaluatorForm(forms.Form):
    section_id = forms.IntegerField(widget=forms.HiddenInput())
    section_title = forms.CharField(disabled=True, required=False, label='Section')
    evaluator = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False,
        label='Assign Evaluator'
    )
