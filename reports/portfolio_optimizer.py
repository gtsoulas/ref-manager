# ============================================================
# FILE: reports/portfolio_optimizer.py
# Portfolio optimization algorithm for REF submissions
# ============================================================

from decimal import Decimal
from itertools import combinations
from django.db.models import Q
import numpy as np


class PortfolioOptimizer:
    """
    Optimize REF submission portfolio based on quality, risk, and diversity metrics.
    
    Uses a combination of:
    - Greedy algorithm for quick solutions
    - Constraint satisfaction for requirements
    - Multi-objective optimization for balanced portfolios
    """
    
    def __init__(self, submission):
        """
        Initialize optimizer with a REF submission.
        
        Args:
            submission: REFSubmission object
        """
        self.submission = submission
        self.all_outputs = None
        
    def suggest_optimal_portfolio(
        self,
        available_outputs,
        min_outputs=None,
        max_outputs=None,
        max_risk=0.60,
        min_quality=3.0,
        require_oa_compliance=True,
        strategy='balanced'
    ):
        """
        Suggest optimal portfolio configuration.
        
        Args:
            available_outputs: QuerySet of available Output objects
            min_outputs: Minimum number of outputs (None = no minimum)
            max_outputs: Maximum number of outputs (None = no maximum)
            max_risk: Maximum acceptable average risk (0-1)
            min_quality: Minimum acceptable average quality (0-4)
            require_oa_compliance: Exclude outputs with OA issues
            strategy: 'balanced', 'quality_focused', 'risk_averse', or 'inclusive'
        
        Returns:
            dict with recommendations and analysis
        """
        self.all_outputs = available_outputs
        
        # Filter outputs based on constraints
        filtered_outputs = self._apply_constraints(
            available_outputs,
            max_risk,
            min_quality,
            require_oa_compliance
        )
        
        if filtered_outputs.count() == 0:
            return {
                'success': False,
                'message': 'No outputs meet the specified constraints',
                'recommended_outputs': [],
                'metrics': {}
            }
        
        # Apply strategy
        if strategy == 'quality_focused':
            recommended = self._quality_focused_selection(
                filtered_outputs, min_outputs, max_outputs
            )
        elif strategy == 'risk_averse':
            recommended = self._risk_averse_selection(
                filtered_outputs, min_outputs, max_outputs
            )
        elif strategy == 'inclusive':
            recommended = self._inclusive_selection(
                filtered_outputs, min_outputs, max_outputs
            )
        else:  # balanced
            recommended = self._balanced_selection(
                filtered_outputs, min_outputs, max_outputs
            )
        
        # Calculate metrics for recommended portfolio
        metrics = self._calculate_portfolio_metrics(recommended)
        
        # Compare with current submission
        comparison = self._compare_with_current(recommended)
        
        return {
            'success': True,
            'message': f'Found optimal portfolio using {strategy} strategy',
            'recommended_outputs': recommended,
            'count': len(recommended),
            'metrics': metrics,
            'comparison': comparison,
            'strategy': strategy
        }
    
    def _apply_constraints(self, outputs, max_risk, min_quality, require_oa):
        """Filter outputs based on hard constraints"""
        filtered = outputs
        
        # OA compliance
        if require_oa:
            filtered = filtered.filter(oa_compliance_risk=False)
        
        # Risk constraint
        filtered = filtered.filter(overall_risk_score__lte=Decimal(str(max_risk)))
        
        # Quality constraint (filter by quality rating)
        if min_quality >= 4:
            filtered = filtered.filter(quality_rating='4*')
        elif min_quality >= 3:
            filtered = filtered.filter(quality_rating__in=['3*', '4*'])
        elif min_quality >= 2:
            filtered = filtered.filter(quality_rating__in=['2*', '3*', '4*'])
        
        return filtered
    
    def _quality_focused_selection(self, outputs, min_outputs, max_outputs):
        """Select outputs prioritizing quality"""
        # Sort by quality first, then by low risk
        sorted_outputs = sorted(
            outputs,
            key=lambda o: (-o.get_quality_value(), o.overall_risk_score)
        )
        
        # Take top outputs
        if max_outputs:
            return sorted_outputs[:max_outputs]
        elif min_outputs:
            return sorted_outputs[:min_outputs]
        else:
            # Take all 4* and 3* outputs
            return [o for o in sorted_outputs if o.get_quality_value() >= 3]
    
    def _risk_averse_selection(self, outputs, min_outputs, max_outputs):
        """Select outputs prioritizing low risk"""
        # Sort by risk first, then by quality
        sorted_outputs = sorted(
            outputs,
            key=lambda o: (o.overall_risk_score, -o.get_quality_value())
        )
        
        if max_outputs:
            return sorted_outputs[:max_outputs]
        elif min_outputs:
            return sorted_outputs[:min_outputs]
        else:
            # Take all outputs with low to medium-low risk
            return [o for o in sorted_outputs if o.overall_risk_score < Decimal('0.50')]
    
    def _inclusive_selection(self, outputs, min_outputs, max_outputs):
        """Select outputs maximizing staff inclusion"""
        # Group by colleague, take best from each
        from collections import defaultdict
        by_colleague = defaultdict(list)
        
        for output in outputs:
            colleague_id = output.colleague.id if hasattr(output, 'colleague') else None
            by_colleague[colleague_id].append(output)
        
        # Take best output from each colleague
        selected = []
        for colleague_outputs in by_colleague.values():
            # Sort by quality and risk
            best = max(
                colleague_outputs,
                key=lambda o: (o.get_quality_value() * 10 - float(o.overall_risk_score))
            )
            selected.append(best)
        
        # Sort selected outputs by composite score
        selected.sort(
            key=lambda o: (o.get_quality_value() * 10 - float(o.overall_risk_score)),
            reverse=True
        )
        
        if max_outputs and len(selected) > max_outputs:
            return selected[:max_outputs]
        elif min_outputs and len(selected) < min_outputs:
            # Add more outputs to meet minimum
            remaining = [o for o in outputs if o not in selected]
            remaining.sort(
                key=lambda o: (o.get_quality_value() * 10 - float(o.overall_risk_score)),
                reverse=True
            )
            needed = min_outputs - len(selected)
            selected.extend(remaining[:needed])
        
        return selected
    
    def _balanced_selection(self, outputs, min_outputs, max_outputs):
        """Select outputs using balanced scoring"""
        # Calculate composite score for each output
        scored_outputs = []
        
        for output in outputs:
            quality = output.get_quality_value()
            risk = float(output.overall_risk_score)
            panel_alignment = float(output.panel_alignment_score)
            venue_prestige = float(output.venue_prestige_score)
            
            # Composite score: weighted combination
            score = (
                quality * 0.40 +  # Quality is most important
                (1 - risk) * 4 * 0.35 +  # Risk (inverted and scaled)
                panel_alignment * 4 * 0.15 +  # Panel alignment (scaled)
                venue_prestige * 4 * 0.10  # Venue prestige (scaled)
            )
            
            scored_outputs.append((output, score))
        
        # Sort by composite score
        scored_outputs.sort(key=lambda x: x[1], reverse=True)
        
        # Select top outputs
        if max_outputs:
            return [o for o, s in scored_outputs[:max_outputs]]
        elif min_outputs:
            return [o for o, s in scored_outputs[:min_outputs]]
        else:
            # Return outputs above threshold score
            threshold = 2.5  # Aim for above-average portfolio
            return [o for o, s in scored_outputs if s >= threshold]
    
    def _calculate_portfolio_metrics(self, outputs):
        """Calculate metrics for a portfolio of outputs"""
        if not outputs:
            return {}
        
        total = len(outputs)
        
        # Quality metrics
        quality_values = [o.get_quality_value() for o in outputs]
        avg_quality = sum(quality_values) / total
        
        quality_dist = {
            '4*': sum(1 for o in outputs if o.quality_rating == '4*'),
            '3*': sum(1 for o in outputs if o.quality_rating == '3*'),
            '2*': sum(1 for o in outputs if o.quality_rating == '2*'),
            '1*': sum(1 for o in outputs if o.quality_rating == '1*'),
        }
        
        # Risk metrics
        risks = [float(o.overall_risk_score) for o in outputs]
        avg_risk = sum(risks) / total
        
        risk_dist = {
            'low': sum(1 for r in risks if r < 0.25),
            'medium_low': sum(1 for r in risks if 0.25 <= r < 0.50),
            'medium_high': sum(1 for r in risks if 0.50 <= r < 0.75),
            'high': sum(1 for r in risks if r >= 0.75),
        }
        
        # Staff diversity
        colleagues = set(
            o.colleague.id for o in outputs 
            if hasattr(o, 'colleague') and o.colleague
        )
        staff_count = len(colleagues)
        
        # OA compliance
        oa_issues = sum(1 for o in outputs if o.oa_compliance_risk)
        
        # REF readiness
        ref_ready = sum(1 for o in outputs if o.is_ref_ready())
        
        return {
            'total_outputs': total,
            'avg_quality': round(avg_quality, 2),
            'avg_risk': round(avg_risk, 2),
            'quality_distribution': quality_dist,
            'risk_distribution': risk_dist,
            'staff_count': staff_count,
            'oa_issues': oa_issues,
            'ref_ready': ref_ready,
            'ref_ready_percentage': round((ref_ready / total) * 100, 1) if total > 0 else 0
        }
    
    def _compare_with_current(self, recommended_outputs):
        """Compare recommended portfolio with current submission"""
        current_outputs = list(self.submission.outputs.all())
        
        if not current_outputs:
            return {
                'has_current': False,
                'message': 'No current outputs to compare'
            }
        
        current_metrics = self._calculate_portfolio_metrics(current_outputs)
        recommended_metrics = self._calculate_portfolio_metrics(recommended_outputs)
        
        # Calculate improvements
        quality_change = (
            recommended_metrics['avg_quality'] - current_metrics['avg_quality']
        )
        risk_change = (
            recommended_metrics['avg_risk'] - current_metrics['avg_risk']
        )
        
        # Identify outputs to add/remove
        current_ids = {o.id for o in current_outputs}
        recommended_ids = {o.id for o in recommended_outputs}
        
        to_add = [o for o in recommended_outputs if o.id not in current_ids]
        to_remove = [o for o in current_outputs if o.id not in recommended_ids]
        
        return {
            'has_current': True,
            'current_metrics': current_metrics,
            'recommended_metrics': recommended_metrics,
            'quality_change': round(quality_change, 2),
            'risk_change': round(risk_change, 2),
            'quality_improved': quality_change > 0.1,
            'risk_improved': risk_change < -0.05,  # Lower risk is better
            'outputs_to_add': to_add,
            'outputs_to_remove': to_remove,
            'count_change': len(recommended_outputs) - len(current_outputs)
        }
    
    def compare_strategies(self, available_outputs, **kwargs):
        """
        Compare different optimization strategies.
        
        Returns recommendations for all strategies.
        """
        strategies = ['balanced', 'quality_focused', 'risk_averse', 'inclusive']
        results = {}
        
        for strategy in strategies:
            results[strategy] = self.suggest_optimal_portfolio(
                available_outputs,
                strategy=strategy,
                **kwargs
            )
        
        return results
    
    def scenario_analysis(
        self,
        available_outputs,
        scenarios=None
    ):
        """
        Perform scenario analysis with different constraints.
        
        Args:
            available_outputs: QuerySet of available outputs
            scenarios: List of scenario dicts, or None for defaults
        
        Returns:
            dict of scenario results
        """
        if scenarios is None:
            scenarios = [
                {
                    'name': 'Conservative',
                    'max_risk': 0.40,
                    'min_quality': 3.0,
                    'strategy': 'risk_averse'
                },
                {
                    'name': 'Balanced',
                    'max_risk': 0.60,
                    'min_quality': 2.5,
                    'strategy': 'balanced'
                },
                {
                    'name': 'Ambitious',
                    'max_risk': 0.75,
                    'min_quality': 2.0,
                    'strategy': 'quality_focused'
                },
                {
                    'name': 'Inclusive',
                    'max_risk': 0.65,
                    'min_quality': 2.5,
                    'strategy': 'inclusive'
                }
            ]
        
        results = {}
        
        for scenario in scenarios:
            name = scenario.pop('name')
            results[name] = self.suggest_optimal_portfolio(
                available_outputs,
                **scenario
            )
        
        return results


# ============================================================
# USAGE EXAMPLES:
# ============================================================
#
# from core.models import Output, REFSubmission
# from reports.portfolio_optimizer import PortfolioOptimizer
#
# # Get submission and available outputs
# submission = REFSubmission.objects.get(id=1)
# available_outputs = Output.objects.all()
#
# # Initialize optimizer
# optimizer = PortfolioOptimizer(submission)
#
# # Get balanced recommendation
# result = optimizer.suggest_optimal_portfolio(
#     available_outputs,
#     max_outputs=50,
#     max_risk=0.60,
#     min_quality=3.0,
#     strategy='balanced'
# )
#
# print(f"Recommended {result['count']} outputs")
# print(f"Average quality: {result['metrics']['avg_quality']}")
# print(f"Average risk: {result['metrics']['avg_risk']}")
#
# # Compare strategies
# comparison = optimizer.compare_strategies(available_outputs, max_outputs=50)
# for strategy, result in comparison.items():
#     print(f"\n{strategy}:")
#     print(f"  Quality: {result['metrics']['avg_quality']}")
#     print(f"  Risk: {result['metrics']['avg_risk']}")
#
# # Scenario analysis
# scenarios = optimizer.scenario_analysis(available_outputs)
# for scenario_name, result in scenarios.items():
#     print(f"\n{scenario_name} Scenario:")
#     print(f"  Outputs: {result['count']}")
#     print(f"  Quality: {result['metrics']['avg_quality']}")
#
