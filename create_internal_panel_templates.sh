#!/bin/bash

echo "Creating Internal Panel Templates..."
echo ""

# Create templates/core/internal_panel_list.html
cat > templates/core/internal_panel_list.html << 'EOF'
{% extends 'base.html' %}

{% block title %}Internal Evaluation Panel - REF Manager{% endblock %}

{% block content %}
<div class="container-fluid">
    <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pb-2 mb-3 border-bottom">
        <h1 class="h2">Internal Evaluation Panel</h1>
        <div class="btn-toolbar mb-2 mb-md-0">
            <a href="{% url 'internal_panel_create' %}" class="btn btn-sm btn-primary">
                <i class="fas fa-plus"></i> Add Panel Member
            </a>
        </div>
    </div>

    <div class="card">
        <div class="card-body">
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Role</th>
                            <th>Expertise Area</th>
                            <th>Appointed</th>
                            <th>Assignments</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for member in panel_members %}
                        <tr>
                            <td>
                                <a href="{% url 'internal_panel_detail' member.pk %}">
                                    {{ member.colleague.user.get_full_name }}
                                </a>
                            </td>
                            <td>{{ member.get_role_display }}</td>
                            <td>{{ member.expertise_area }}</td>
                            <td>{{ member.appointed_date|date:"d M Y" }}</td>
                            <td>{{ member.internalpanelassignment_set.count }}</td>
                            <td>
                                {% if member.is_active %}
                                    <span class="badge bg-success">Active</span>
                                {% else %}
                                    <span class="badge bg-secondary">Inactive</span>
                                {% endif %}
                            </td>
                            <td>
                                <a href="{% url 'internal_panel_detail' member.pk %}" class="btn btn-sm btn-info">
                                    <i class="fas fa-eye"></i>
                                </a>
                                <a href="{% url 'internal_panel_update' member.pk %}" class="btn btn-sm btn-warning">
                                    <i class="fas fa-edit"></i>
                                </a>
                            </td>
                        </tr>
                        {% empty %}
                        <tr>
                            <td colspan="7" class="text-center text-muted">No panel members found.</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>
{% endblock %}
EOF
echo "✓ Created internal_panel_list.html"

# Create templates/core/internal_panel_detail.html
cat > templates/core/internal_panel_detail.html << 'EOF'
{% extends 'base.html' %}

{% block title %}{{ panel_member.colleague.user.get_full_name }} - REF Manager{% endblock %}

{% block content %}
<div class="container-fluid">
    <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pb-2 mb-3 border-bottom">
        <h1 class="h2">{{ panel_member.colleague.user.get_full_name }}</h1>
        <div class="btn-toolbar mb-2 mb-md-0">
            <a href="{% url 'internal_panel_update' panel_member.pk %}" class="btn btn-sm btn-warning">
                <i class="fas fa-edit"></i> Edit
            </a>
            <a href="{% url 'internal_panel_list' %}" class="btn btn-sm btn-outline-secondary">
                <i class="fas fa-arrow-left"></i> Back to List
            </a>
        </div>
    </div>

    <div class="row">
        <div class="col-md-8">
            <div class="card mb-3">
                <div class="card-header">
                    <h5 class="card-title mb-0">Panel Member Information</h5>
                </div>
                <div class="card-body">
                    <dl class="row">
                        <dt class="col-sm-4">Name:</dt>
                        <dd class="col-sm-8">{{ panel_member.colleague.user.get_full_name }}</dd>

                        <dt class="col-sm-4">Staff ID:</dt>
                        <dd class="col-sm-8">{{ panel_member.colleague.staff_id }}</dd>

                        <dt class="col-sm-4">Email:</dt>
                        <dd class="col-sm-8">{{ panel_member.colleague.user.email }}</dd>

                        <dt class="col-sm-4">Role:</dt>
                        <dd class="col-sm-8">{{ panel_member.get_role_display }}</dd>

                        <dt class="col-sm-4">Expertise Area:</dt>
                        <dd class="col-sm-8">{{ panel_member.expertise_area }}</dd>

                        <dt class="col-sm-4">Appointed:</dt>
                        <dd class="col-sm-8">{{ panel_member.appointed_date|date:"d M Y" }}</dd>

                        <dt class="col-sm-4">Status:</dt>
                        <dd class="col-sm-8">
                            {% if panel_member.is_active %}
                                <span class="badge bg-success">Active</span>
                            {% else %}
                                <span class="badge bg-secondary">Inactive</span>
                            {% endif %}
                        </dd>

                        {% if panel_member.notes %}
                        <dt class="col-sm-4">Notes:</dt>
                        <dd class="col-sm-8">{{ panel_member.notes }}</dd>
                        {% endif %}
                    </dl>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <h5 class="card-title mb-0">Assigned Outputs</h5>
                </div>
                <div class="card-body">
                    {% if assignments %}
                    <div class="table-responsive">
                        <table class="table table-sm">
                            <thead>
                                <tr>
                                    <th>Output</th>
                                    <th>Status</th>
                                    <th>Assigned</th>
                                    <th>Rating Rec.</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for assignment in assignments %}
                                <tr>
                                    <td>
                                        <a href="{% url 'output_detail' assignment.output.pk %}">
                                            {{ assignment.output.title|truncatewords:10 }}
                                        </a>
                                    </td>
                                    <td>
                                        <span class="badge bg-info">{{ assignment.get_status_display }}</span>
                                    </td>
                                    <td>{{ assignment.assigned_date|date:"d M Y" }}</td>
                                    <td>
                                        {% if assignment.rating_recommendation %}
                                            <span class="badge bg-success">{{ assignment.rating_recommendation }}</span>
                                        {% else %}
                                            <span class="text-muted">-</span>
                                        {% endif %}
                                    </td>
                                    <td>
                                        <a href="{% url 'internal_panel_assignment_update' assignment.pk %}" class="btn btn-sm btn-warning">
                                            <i class="fas fa-edit"></i>
                                        </a>
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                    {% else %}
                    <p class="text-muted">No outputs assigned yet.</p>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
EOF
echo "✓ Created internal_panel_detail.html"

# Create templates/core/internal_panel_form.html
cat > templates/core/internal_panel_form.html << 'EOF'
{% extends 'base.html' %}
{% load crispy_forms_tags %}

{% block title %}{% if panel_member %}Edit{% else %}Add{% endif %} Panel Member - REF Manager{% endblock %}

{% block content %}
<div class="container-fluid">
    <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pb-2 mb-3 border-bottom">
        <h1 class="h2">{% if panel_member %}Edit{% else %}Add{% endif %} Internal Panel Member</h1>
        <div class="btn-toolbar mb-2 mb-md-0">
            <a href="{% url 'internal_panel_list' %}" class="btn btn-sm btn-outline-secondary">
                <i class="fas fa-arrow-left"></i> Back to List
            </a>
        </div>
    </div>

    <div class="row">
        <div class="col-md-8">
            <div class="card">
                <div class="card-body">
                    <form method="post">
                        {% csrf_token %}
                        {{ form|crispy }}
                        <div class="mt-3">
                            <button type="submit" class="btn btn-primary">
                                <i class="fas fa-save"></i> Save
                            </button>
                            <a href="{% url 'internal_panel_list' %}" class="btn btn-secondary">
                                <i class="fas fa-times"></i> Cancel
                            </a>
                        </div>
                    </form>
                </div>
            </div>
        </div>

        <div class="col-md-4">
            <div class="card">
                <div class="card-header">
                    <h5 class="card-title mb-0">Panel Roles</h5>
                </div>
                <div class="card-body">
                    <dl class="small">
                        <dt>Panel Chair</dt>
                        <dd>Leads the evaluation panel</dd>

                        <dt>Panel Member</dt>
                        <dd>Regular panel member</dd>

                        <dt>Subject Specialist</dt>
                        <dd>Expert in specific research area</dd>

                        <dt>External Liaison</dt>
                        <dd>Coordinates with external reviewers</dd>
                    </dl>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
EOF
echo "✓ Created internal_panel_form.html"

# Create templates/core/assign_internal_panel.html
cat > templates/core/assign_internal_panel.html << 'EOF'
{% extends 'base.html' %}
{% load crispy_forms_tags %}

{% block title %}Assign Internal Panel - REF Manager{% endblock %}

{% block content %}
<div class="container-fluid">
    <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pb-2 mb-3 border-bottom">
        <h1 class="h2">Assign Internal Panel Member</h1>
        <div class="btn-toolbar mb-2 mb-md-0">
            <a href="{% url 'output_detail' output.pk %}" class="btn btn-sm btn-outline-secondary">
                <i class="fas fa-arrow-left"></i> Back to Output
            </a>
        </div>
    </div>

    <div class="row">
        <div class="col-md-8">
            <div class="card mb-3">
                <div class="card-header">
                    <h5 class="card-title mb-0">Output Details</h5>
                </div>
                <div class="card-body">
                    <dl class="row">
                        <dt class="col-sm-3">Title:</dt>
                        <dd class="col-sm-9">{{ output.title }}</dd>

                        <dt class="col-sm-3">Author:</dt>
                        <dd class="col-sm-9">{{ output.colleague.user.get_full_name }}</dd>

                        <dt class="col-sm-3">Type:</dt>
                        <dd class="col-sm-9">{{ output.get_publication_type_display }}</dd>
                    </dl>
                </div>
            </div>

            <div class="card">
                <div class="card-body">
                    <form method="post">
                        {% csrf_token %}
                        {{ form|crispy }}
                        <div class="mt-3">
                            <button type="submit" class="btn btn-primary">
                                <i class="fas fa-user-plus"></i> Assign Panel Member
                            </button>
                            <a href="{% url 'output_detail' output.pk %}" class="btn btn-secondary">
                                <i class="fas fa-times"></i> Cancel
                            </a>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
EOF
echo "✓ Created assign_internal_panel.html"

# Create templates/core/internal_panel_assignment_form.html
cat > templates/core/internal_panel_assignment_form.html << 'EOF'
{% extends 'base.html' %}
{% load crispy_forms_tags %}

{% block title %}Update Assignment - REF Manager{% endblock %}

{% block content %}
<div class="container-fluid">
    <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pb-2 mb-3 border-bottom">
        <h1 class="h2">Update Internal Panel Assignment</h1>
        <div class="btn-toolbar mb-2 mb-md-0">
            <a href="{% url 'output_detail' assignment.output.pk %}" class="btn btn-sm btn-outline-secondary">
                <i class="fas fa-arrow-left"></i> Back to Output
            </a>
        </div>
    </div>

    <div class="row">
        <div class="col-md-8">
            <div class="card mb-3">
                <div class="card-header">
                    <h5 class="card-title mb-0">Assignment Details</h5>
                </div>
                <div class="card-body">
                    <dl class="row">
                        <dt class="col-sm-3">Output:</dt>
                        <dd class="col-sm-9">{{ assignment.output.title }}</dd>

                        <dt class="col-sm-3">Panel Member:</dt>
                        <dd class="col-sm-9">{{ assignment.panel_member }}</dd>

                        <dt class="col-sm-3">Assigned:</dt>
                        <dd class="col-sm-9">{{ assignment.assigned_date|date:"d M Y" }}</dd>
                    </dl>
                </div>
            </div>

            <div class="card">
                <div class="card-body">
                    <form method="post">
                        {% csrf_token %}
                        {{ form|crispy }}
                        <div class="mt-3">
                            <button type="submit" class="btn btn-primary">
                                <i class="fas fa-save"></i> Update Assignment
                            </button>
                            <a href="{% url 'output_detail' assignment.output.pk %}" class="btn btn-secondary">
                                <i class="fas fa-times"></i> Cancel
                            </a>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
EOF
echo "✓ Created internal_panel_assignment_form.html"

echo ""
echo "=========================================="
echo "✓ All 5 templates created successfully!"
echo "=========================================="
echo ""
echo "Templates created:"
echo "  1. templates/core/internal_panel_list.html"
echo "  2. templates/core/internal_panel_detail.html"
echo "  3. templates/core/internal_panel_form.html"
echo "  4. templates/core/assign_internal_panel.html"
echo "  5. templates/core/internal_panel_assignment_form.html"
echo ""
