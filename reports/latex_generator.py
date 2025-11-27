from django.template import Template, Context
from django.utils import timezone
from core.models import Output, Colleague


class LaTeXGenerator:
    """Generate LaTeX source files from Django templates"""
    
    def __init__(self, document_class='article'):
        """
        Initialize LaTeX generator
        
        Args:
            document_class: 'article', 'report', or 'beamer'
        """
        if document_class not in ['article', 'report', 'beamer']:
            raise ValueError(f"Invalid document class. Choose from: article, report, beamer")
        
        self.document_class = document_class
    
    def latex_escape(self, text):
        """Escape special LaTeX characters"""
        if text is None:
            return ''
        
        text = str(text)
        replacements = {
            '&': r'\&',
            '%': r'\%',
            '$': r'\$',
            '#': r'\#',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
            '~': r'\textasciitilde{}',
            '^': r'\textasciicircum{}',
            '\\': r'\textbackslash{}',
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text
    
    def generate_submission_overview(self, title="REF Submission Overview", author="REF Manager"):
        """Generate submission overview report"""
        outputs = Output.objects.all().select_related('colleague__user')
        colleagues = Colleague.objects.all().select_related('user')
        
        if self.document_class == 'beamer':
            content = self._generate_beamer_submission_content(outputs, colleagues)
        else:
            content = self._generate_article_submission_content(outputs, colleagues)
        
        return self._render_template(title, author, content)
    
    def generate_quality_profile(self, title="Quality Profile Report", author="REF Manager"):
        """Generate quality profile report"""
        outputs = Output.objects.all()
        
        quality_counts = {
            '4*': outputs.filter(quality_rating='4*').count(),
            '3*': outputs.filter(quality_rating='3*').count(),
            '2*': outputs.filter(quality_rating='2*').count(),
            '1*': outputs.filter(quality_rating='1*').count(),
            'U': outputs.filter(quality_rating='U').count(),
        }
        
        if self.document_class == 'beamer':
            content = self._generate_beamer_quality_content(quality_counts, outputs)
        else:
            content = self._generate_article_quality_content(quality_counts, outputs)
        
        return self._render_template(title, author, content)
    
    def generate_staff_progress(self, title="Staff Progress Report", author="REF Manager"):
        """Generate staff progress report"""
        colleagues = Colleague.objects.all().prefetch_related('outputs')
        
        if self.document_class == 'beamer':
            content = self._generate_beamer_staff_content(colleagues)
        else:
            content = self._generate_article_staff_content(colleagues)
        
        return self._render_template(title, author, content)
    
    def _render_template(self, title, author, content, institution="University"):
        """Render the main LaTeX template with content"""
        title_escaped = self.latex_escape(title)
        author_escaped = self.latex_escape(author)
        date = timezone.now().strftime('%B %d, %Y')
        
        if self.document_class == 'beamer':
            template = r'''\documentclass[11pt]{beamer}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{booktabs}
\usepackage{graphicx}

\usetheme{Madrid}
\usecolortheme{default}

\title{''' + title_escaped + r'''}
\author{''' + author_escaped + r'''}
\date{''' + date + r'''}

\begin{document}

\frame{\titlepage}

\begin{frame}
\frametitle{Contents}
\tableofcontents
\end{frame}

''' + content + r'''

\end{document}'''
        else:
            doc_type = self.document_class
            template = r'''\documentclass[11pt,a4paper]{''' + doc_type + r'''}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{geometry}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{graphicx}
\usepackage{hyperref}

\geometry{margin=2.5cm}
\setlength{\parindent}{0pt}
\setlength{\parskip}{6pt}

\title{''' + title_escaped + r'''}
\author{''' + author_escaped + r'''}
\date{''' + date + r'''}

\begin{document}

\maketitle
\tableofcontents
\newpage

''' + content + r'''

\end{document}'''
        
        return template
    
    def _generate_article_submission_content(self, outputs, colleagues):
        """Generate article/report content for submission overview"""
        content = r'''\section{Executive Summary}

This report provides a comprehensive overview of the REF submission preparation status.

\subsection{Key Statistics}

\begin{itemize}
'''
        content += f"\\item Total Staff Members: {colleagues.count()}\n"
        content += f"\\item Total Outputs: {outputs.count()}\n"
        content += f"\\item Returnable Staff: {colleagues.filter(is_returnable=True).count()}\n"
        content += r'''\end{itemize}

\section{Output Summary by Quality}

\begin{table}[h]
\centering
\begin{tabular}{lrrr}
\toprule
Quality & Count & Percentage & Cumulative \\
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
\caption{Output distribution by quality rating}
\end{table}

\section{Staff Returns}

\begin{longtable}{llrr}
\toprule
Staff Name & Unit & FTE & Outputs \\
\midrule
\endhead
'''
        
        for colleague in colleagues[:20]:
            name = self.latex_escape(colleague.user.get_full_name())
            unit = self.latex_escape(colleague.unit_of_assessment[:30])
            fte = colleague.fte
            output_count = colleague.outputs.count()  # FIXED: changed from output_set to outputs
            content += f"{name} & {unit} & {fte} & {output_count} \\\\\n"
        
        content += r'''\bottomrule
\end{longtable}

\section{Recommendations}

Based on the current data:

\begin{enumerate}
\item Continue to focus on quality improvement for outputs currently rated 2* or below
\item Ensure all returnable staff have a minimum of 1 output prepared
\item Complete critical friend reviews for all 3* and 4* outputs
\item Monitor staff progress and provide support where needed
\end{enumerate}
'''
        return content
    
    def _generate_article_quality_content(self, quality_counts, outputs):
        """Generate quality profile content"""
        content = r'''\section{Quality Profile Analysis}

\subsection{Distribution Overview}

\begin{table}[h]
\centering
\begin{tabular}{lrr}
\toprule
Rating & Count & Percentage \\
\midrule
'''
        total = sum(quality_counts.values()) or 1
        for rating, count in quality_counts.items():
            pct = (count / total) * 100
            content += f"{rating} & {count} & {pct:.1f}\\% \\\\\n"
        
        content += r'''\bottomrule
\end{tabular}
\caption{Quality rating distribution}
\end{table}

\subsection{Outputs by Type}

'''
        publication_types = outputs.values_list('publication_type', flat=True).distinct()
        for out_type in publication_types:
            type_outputs = outputs.filter(publication_type=out_type)
            escaped_type = self.latex_escape(out_type)
            content += f"\\subsubsection{{{escaped_type}}}\n\n"
            content += f"Total: {type_outputs.count()} outputs\n\n"
        
        return content
    
    def _generate_article_staff_content(self, colleagues):
        """Generate staff progress content"""
        content = r'''\section{Staff Progress Report}

\subsection{Individual Progress}

\begin{longtable}{lrrr}
\toprule
Staff Member & Outputs & 4*/3* Count & Progress \\
\midrule
\endhead
'''
        
        for colleague in colleagues:
            name = self.latex_escape(colleague.user.get_full_name())
            total_outputs = colleague.outputs.count()  # FIXED: changed from output_set to outputs
            high_quality = colleague.outputs.filter(quality_rating__in=['4*', '3*']).count()  # FIXED
            progress = "Yes" if total_outputs >= 1 else "No"
            content += f"{name} & {total_outputs} & {high_quality} & {progress} \\\\\n"
        
        content += r'''\bottomrule
\end{longtable}
'''
        return content
    
    def _generate_beamer_submission_content(self, outputs, colleagues):
        """Generate beamer slides for submission overview"""
        content = r'''\section{Overview}

\begin{frame}
\frametitle{Key Statistics}
\begin{itemize}
'''
        content += f"\\item Total Staff Members: {colleagues.count()}\n"
        content += f"\\item Total Outputs: {outputs.count()}\n"
        content += f"\\item Returnable Staff: {colleagues.filter(is_returnable=True).count()}\n"
        content += r'''\end{itemize}
\end{frame}

\section{Quality Profile}

\begin{frame}
\frametitle{Output Quality Distribution}
\begin{table}
\begin{tabular}{lr}
\toprule
Rating & Count \\
\midrule
'''
        for rating in ['4*', '3*', '2*', '1*', 'U']:
            count = outputs.filter(quality_rating=rating).count()
            content += f"{rating} & {count} \\\\\n"
        
        content += r'''\bottomrule
\end{tabular}
\end{table}
\end{frame}
'''
        return content
    
    def _generate_beamer_quality_content(self, quality_counts, outputs):
        """Generate beamer slides for quality profile"""
        content = r'''\section{Quality Analysis}

\begin{frame}
\frametitle{Quality Distribution}
\begin{table}
\begin{tabular}{lrr}
\toprule
Rating & Count & Percentage \\
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
    
    def _generate_beamer_staff_content(self, colleagues):
        """Generate beamer slides for staff progress"""
        content = r'''\section{Staff Progress}

\begin{frame}
\frametitle{Individual Progress}
\begin{table}
\scriptsize
\begin{tabular}{lrr}
\toprule
Staff & Outputs & High Quality \\
\midrule
'''
        for colleague in colleagues[:15]:
            name = self.latex_escape(colleague.user.get_full_name()[:20])
            total = colleague.outputs.count()  # FIXED: changed from output_set to outputs
            high_q = colleague.outputs.filter(quality_rating__in=['4*', '3*']).count()  # FIXED
            content += f"{name} & {total} & {high_q} \\\\\n"
        
        content += r'''\bottomrule
\end{tabular}
\end{table}
\end{frame}
'''
        return content

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
