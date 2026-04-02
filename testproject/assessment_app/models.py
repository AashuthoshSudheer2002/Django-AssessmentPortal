from django.db import models
from django.core.validators import MinValueValidator,MaxValueValidator
from django.db.models import *
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
# Create your models here.
class Section(models.Model):
    title = models.CharField(max_length=40,null=False,blank=False,unique=True)

    def __str__(self):
        return self.title

class Role(models.Model):
    title = models.CharField(max_length=40,null=False,blank=False,unique=True)
    
    def __str__(self):
        return self.title

class SectionWeight(models.Model):
    section = models.ForeignKey(Section,on_delete=models.CASCADE,related_name='weights')
    weight = models.IntegerField(validators=[MinValueValidator(0)])
    role = models.ForeignKey(Role,on_delete=models.CASCADE)

    class Meta:
        unique_together= ('section','role','weight')
    def __str__(self):
        return f"{self.role.title} -> {self.section.title} -> {self.weight}%"
    
    def clean(self):
        section = self.section
        role = self.role
        weight = self.weight

        if section and role and weight is not None:
            current_total = SectionWeight.objects.filter(role=role).exclude(pk=self.pk).aggregate(
                total=models.Sum('weight')
            )['total'] or 0  # Default to 0 if no existing weights are found

            remaining = 100 - current_total

            if weight > remaining:
                raise ValidationError(f"Only {remaining}% weight left for section '{section.title}' and role '{role.title}'.")
            
    def save(self,*args,**kwargs):
        self.full_clean()
        return super().save(*args,**kwargs)

class Candidate(models.Model):
    name = models.CharField(max_length=30,null=False,blank=False)
    email = models.EmailField(null=False,blank=False)
    resume = models.FileField(upload_to="resumes/",blank=True,null=True)
    role = models.ForeignKey(Role,related_name='candidaterole',on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
class Evaluator(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate,on_delete=models.CASCADE)
    section = models.ForeignKey(Section,related_name='evalsect',on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user','candidate')
        permissions = [
            # CandidateCriterionScore permissions
            ("add_candidatecriterionscore", "Can add Candidate Criterion Score"),
            ("change_candidatecriterionscore", "Can change Candidate Criterion Score"),
            ("delete_candidatecriterionscore", "Can delete Candidate Criterion Score"),
            ("view_candidatecriterionscore", "Can view Candidate Criterion Score"),

            # Additional 'view' permissions for other models (manually added)
            ("view_candidate", "Can view Candidate"),
            ("view_section", "Can view Section"),
            ("view_criteria", "Can view Criteria"),
            ("view_criteriaweight", "Can view Criteria Weight"),
            ("view_sectionweight", "Can view Section Weight"),
            # Add more if needed
        ]
    def __str__(self):
        return f"{self.section} -> {self.user.username} -> {self.candidate}"
    
    
   
class Criteria(models.Model):
    criteria_title = models.CharField(max_length=100)
    criteria_section = models.ForeignKey(Section, related_name='criteria', on_delete=models.CASCADE)
    criteria_description = models.TextField()



    def __str__(self):
        return self.criteria_title

    


class CriteriaWeight(models.Model):
    criteria = models.ForeignKey(Criteria,on_delete=models.CASCADE)
    weight = models.IntegerField(validators=[MinValueValidator(0)])
    role = models.ForeignKey(Role,on_delete=models.CASCADE)

    class Meta:
        unique_together= ('criteria','role','weight')
    
    def __str__(self):
        return self.criteria.criteria_title


def clean(self):
    criteria = self.criteria
    role = self.role
    weight = self.weight

    if criteria and role and weight is not None:
        section = criteria.criteria_section  # the section to which this criterion belongs

        # Get all criteria in this section
        section_criteria_ids = Criteria.objects.filter(criteria_section=section).values_list('id', flat=True)

        # Total weight already assigned to these criteria for this role
        current_total = CriteriaWeight.objects.filter(
            role=role,
            criteria_id__in=section_criteria_ids
        ).exclude(pk=self.pk).aggregate(total=models.Sum('weight'))['total'] or 0

        remaining = 100 - current_total

        if weight > remaining:
            raise ValidationError(
                f"Only {remaining}% weight left for criteria '{criteria}' in section '{section}' and role '{role.title}'."
            )


class CandidateCriterionScore(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    criterion = models.ForeignKey(CriteriaWeight, on_delete=models.CASCADE)
    score = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)])
    evaluator = models.ForeignKey(Evaluator, on_delete=models.CASCADE)
    is_evaluated = models.BooleanField(null=True,blank=True,default=False)


    def __str__(self):
        return f"{self.candidate}\t\t{self.criterion}\t\t{self.score}\t\t{self.evaluator}"
