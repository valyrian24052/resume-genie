"""Forms for resume customization."""

from django import forms


class JobCustomizationForm(forms.Form):
    """Simplified form for job-based resume customization."""
    
    openai_api_key = forms.CharField(
        max_length=200,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your OpenAI API key'
        }),
        help_text='Your API key is not stored and only used for this session.'
    )
    
    job_post = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 15,
            'placeholder': 'Paste the entire job posting here from LinkedIn, Indeed, or any job site...\n\nExample:\n"Senior Python Developer at Tech Corp\n\nWe are looking for an experienced Python developer to join our team...\n\nRequirements:\n- 5+ years Python experience\n- Django framework\n- REST API development\n\nPreferred:\n- AWS experience\n- Docker knowledge"'
        }),
        help_text='Paste the complete job posting. AI will automatically extract job title, company, requirements, and other details.'
    )