#!/bin/bash

echo "=========================================="
echo "Installing Comprehensive Report Feature"
echo "=========================================="
echo ""

# Step 1: Add methods to latex_generator.py
echo "Step 1: Adding comprehensive report methods to latex_generator.py..."

# Create the methods in a temp file
cat > /tmp/comprehensive_methods.txt << 'METHODS'

    def generate_comprehensive_report(self, title="REF Comprehensive Report", author="REF Manager"):
        """Generate a comprehensive report combining all sections"""
        outputs = Output.objects.all().select_related('colleague__user')
        colleagues = Colleague.objects.all().select_related('user')
        
        quality_counts = {
            '4*': outputs.filter(quality_rating='4*').count(),
            '3*': outputs.filter(quality_rating='3*').count(),
            '2*': outputs.filter(quality_rating='2*').count(),
            '1*': outputs.filter(quality_rating='1*').count(),
            'U': outputs.filter(quality_rating='U').count(),
        }
        
        if self.document_class == 'beamer':
            content = self._generate_beamer_comprehensive_content(outputs, colleagues, quality_counts)
        else:
            content = self._generate_article_comprehensive_content(outputs, colleagues, quality_counts)
        
        return self._render_template(title, author, content)
    
    def _generate_article_comprehensive_content(self, outputs, colleagues, quality_counts):
        """Generate comprehensive report content"""
        content = r'''\chapter{Executive Summary}

This comprehensive report provides a complete overview of the REF submission preparation.

\section{Key Highlights}

\begin{itemize}
'''
        content += f"\\item Total Staff Members: {colleagues.count()}\n"
        content += f"\\item Returnable Staff: {colleagues.filter(is_returnable=True).count()}\n"
        content += f"\\item Total Outputs: {outputs.count()}\n"
        high_quality = outputs.filter(quality_rating__in=['4*', '3*']).count()
        content += f"\\item High Quality Outputs (4*/3*): {high_quality}\n"
        if outputs.count() > 0:
            pct = (high_quality / outputs.count()) * 100
            content += f"\\item Percentage 4*/3*: {pct:.1f}\\%\n"
        content += r'''\end{itemize}


\chapter{Submission Overview}

\section{Overview Statistics}

\begin{table}[h]
\centering
\begin{tabular}{lr}
\toprule
\textbf{Metric} & \textbf{Count} \\
\midrule
'''
        content += f"Total Staff Members & {colleagues.count()} \\\\\n"
        content += f"Returnable Staff & {colleagues.filter(is_returnable=True).count()} \\\\\n"
        content += f"Total Outputs & {outputs.count()} \\\\\n"
        avg = outputs.count() / colleagues.filter(is_returnable=True).count() if colleagues.filter(is_returnable=True).count() > 0 else 0
        content += f"Average Outputs per Staff & {avg:.2f} \\\\\n"
        content += r'''\bottomrule
\end{tabular}
\caption{Overall Statistics}
\end{table}

\section{Quality Distribution}

\begin{table}[h]
\centering
\begin{tabular}{lrrr}
\toprule
\textbf{Quality} & \textbf{Count} & \textbf{Percentage} & \textbf{Cumulative} \\
\midrule
'''
        total = outputs.count() or 1
        cumulative = 0
        for rating in ['4*', '3*', '2*', '1*', 'U']:
            count = outputs.filter(quality_rating=rating).count()
            pct = (count / total) * 100
            cumulative += count
            cum_pct = (cumulative / total) * 100
            content += f"{rating} & {count} & {pct:.1f}\\% & {cum_pct:.1f}\\% \\\\\n"
        
        content += r'''\bottomrule
\end{tabular}
\caption{Quality Distribution}
\end{table}


\chapter{Staff Progress}

\section{Individual Progress}

\begin{longtable}{lrrrr}
\toprule
\textbf{Staff} & \textbf{Total} & \textbf{4*/3*} & \textbf{2*/1*} & \textbf{Status} \\
\midrule
\endhead
'''
        
        for colleague in colleagues.filter(is_returnable=True):
            name = self.latex_escape(colleague.user.get_full_name()[:30])
            total_outputs = colleague.outputs.count()
            high = colleague.outputs.filter(quality_rating__in=['4*', '3*']).count()
            mid = colleague.outputs.filter(quality_rating__in=['2*', '1*']).count()
            status = "On Track" if total_outputs >= 1 else "Attention"
            content += f"{name} & {total_outputs} & {high} & {mid} & {status} \\\\\n"
        
        content += r'''\bottomrule
\end{longtable}


\chapter{Recommendations}

\section{Key Actions}

\begin{enumerate}
\item Focus on quality improvement for outputs rated 2* or below
\item Ensure all returnable staff have minimum required outputs
\item Complete critical friend and internal panel reviews
\item Finalize submission documentation
\end{enumerate}
'''
        return content
    
    def _generate_beamer_comprehensive_content(self, outputs, colleagues, quality_counts):
        """Generate beamer slides"""
        content = r'''\section{Overview}

\begin{frame}
\frametitle{Executive Summary}
\begin{itemize}
'''
        content += f"\\item Total Staff: {colleagues.count()}\n"
        content += f"\\item Returnable Staff: {colleagues.filter(is_returnable=True).count()}\n"
        content += f"\\item Total Outputs: {outputs.count()}\n"
        high = outputs.filter(quality_rating__in=['4*', '3*']).count()
        content += f"\\item High Quality (4*/3*): {high}\n"
        content += r'''\end{itemize}
\end{frame}

\section{Quality}

\begin{frame}
\frametitle{Quality Distribution}
\begin{table}
\begin{tabular}{lrr}
\toprule
\textbf{Rating} & \textbf{Count} & \textbf{\%} \\
\midrule
'''
        total = sum(quality_counts.values()) or 1
        for rating, count in quality_counts.items():
            pct = (count / total) * 100
            content += f"{rating} & {count} & {pct:.1f}\\% \\\\\n"
        
        content += r'''\bottomrule
\end{tabular}
\end{table}
\end{frame}
'''
        return content
METHODS

# Append to latex_generator.py (before the last line of the class)
# Find the last method and append after it
cat /tmp/comprehensive_methods.txt >> reports/latex_generator.py
echo "✓ Added comprehensive report methods"

# Step 2: Add view to reports/views.py
echo "Step 2: Adding view to reports/views.py..."

if ! grep -q "comprehensive_report" reports/views.py; then
    cat >> reports/views.py << 'EOF'


@login_required
def comprehensive_report(request):
    """Generate comprehensive combined report"""
    doc_class = request.GET.get('format', 'report')
    
    generator = LaTeXGenerator(document_class=doc_class)
    latex_source = generator.generate_comprehensive_report()
    
    response = HttpResponse(latex_source, content_type='text/plain; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="comprehensive_report.tex"'
    return response
EOF
    echo "✓ Added comprehensive_report view"
else
    echo "✓ View already exists"
fi

# Step 3: Add URL
echo "Step 3: Adding URL to reports/urls.py..."

if ! grep -q "comprehensive" reports/urls.py; then
    # Add before the closing bracket
    sed -i "/^]$/i\\    path('comprehensive/', views.comprehensive_report, name='comprehensive')," reports/urls.py
    echo "✓ Added URL"
else
    echo "✓ URL already exists"
fi

# Step 4: Update reports home template
echo "Step 4: Updating reports home template..."

# Create new card for comprehensive report
cat > /tmp/comprehensive_card.html << 'CARD'

        <!-- Comprehensive Report Card -->
        <div class="col-md-12 mb-4">
            <div class="card border-primary">
                <div class="card-header bg-primary text-white">
                    <h5 class="card-title mb-0">
                        <i class="fas fa-file-pdf"></i> Comprehensive Report (ALL SECTIONS)
                    </h5>
                </div>
                <div class="card-body">
                    <p class="card-text">
                        <strong>Complete combined report</strong> including submission overview, quality profile, 
                        staff progress, and review status all in one document.
                    </p>
                    <div class="alert alert-info mb-3">
                        <i class="fas fa-info-circle"></i>
                        <strong>Recommended for final submission:</strong> This generates a comprehensive 
                        multi-chapter document with all sections.
                    </div>
                    <div class="btn-group" role="group">
                        <a href="{% url 'reports:comprehensive' %}?format=article" class="btn btn-primary">
                            <i class="fas fa-file-alt"></i> Article
                        </a>
                        <a href="{% url 'reports:comprehensive' %}?format=report" class="btn btn-primary">
                            <i class="fas fa-file"></i> Report (Recommended)
                        </a>
                        <a href="{% url 'reports:comprehensive' %}?format=beamer" class="btn btn-primary">
                            <i class="fas fa-desktop"></i> Beamer
                        </a>
                    </div>
                </div>
            </div>
        </div>
CARD

# Check if comprehensive report card already exists
if ! grep -q "Comprehensive Report (ALL SECTIONS)" templates/reports/home.html; then
    # Insert before the "How to Use" section
    if grep -q "How to Use Beamer Presentations" templates/reports/home.html; then
        # Insert before that section
        sed -i '/How to Use Beamer Presentations/r /tmp/comprehensive_card.html' templates/reports/home.html
        echo "✓ Added comprehensive report card to reports home"
    else
        # Just append before </div> that closes the row
        # This is trickier - let's just inform the user
        echo "⚠ Please manually add the comprehensive report card to templates/reports/home.html"
        echo "  Card content is in /tmp/comprehensive_card.html"
    fi
else
    echo "✓ Comprehensive report card already exists"
fi

echo ""
echo "=========================================="
echo "✓ Installation Complete!"
echo "=========================================="
echo ""
echo "Comprehensive Report has been installed!"
echo ""
echo "Next steps:"
echo "1. Restart the server: python manage.py runserver"
echo "2. Go to: http://localhost:8000/reports/"
echo "3. You should see a new 'Comprehensive Report' card"
echo "4. Click any format button to download the complete report"
echo ""
echo "Note: The comprehensive report includes:"
echo "  - Executive Summary"
echo "  - Submission Overview"
echo "  - Quality Distribution"
echo "  - Staff Progress"
echo "  - Recommendations"
echo ""
