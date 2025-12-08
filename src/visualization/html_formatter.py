"""HTML formatting for statistics and quality metrics"""

from typing import Dict


class HTMLFormatter:
    """Formats statistics and quality metrics as HTML"""
    
    @staticmethod
    def format_statistics(stats: Dict) -> str:
        """
        Format statistics into a readable HTML string with dark theme
        
        Args:
            stats: Statistics dictionary from DiffHighlighter
            
        Returns:
            HTML string
        """
        html = f"""
        <div style="padding: 15px; background: #000000; border-radius: 10px; color: white; margin: 10px 0;">
            <h3 style="margin-top: 0; color: white;">📊 Change Analysis</h3>

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin: 15px 0;">
                <div style="background: rgba(255,255,255,0.05); padding: 10px; border-radius: 8px; text-align: center;">
                    <div style="font-size: 24px; font-weight: bold;">{stats['total_original']}</div>
                    <div style="font-size: 12px; opacity: 0.8;">Original Words</div>
                </div>
                <div style="background: rgba(255,255,255,0.05); padding: 10px; border-radius: 8px; text-align: center;">
                    <div style="font-size: 24px; font-weight: bold;">{stats['total_generated']}</div>
                    <div style="font-size: 12px; opacity: 0.8;">Generated Words</div>
                </div>
                <div style="background: rgba(255,255,255,0.05); padding: 10px; border-radius: 8px; text-align: center;">
                    <div style="font-size: 24px; font-weight: bold; color: #90EE90;">{stats['unchanged']}</div>
                    <div style="font-size: 12px; opacity: 0.8;">Unchanged</div>
                </div>
                <div style="background: rgba(255,255,255,0.05); padding: 10px; border-radius: 8px; text-align: center;">
                    <div style="font-size: 24px; font-weight: bold; color: #FF4C4C;">{stats['changed']}</div>
                    <div style="font-size: 12px; opacity: 0.8;">Changed</div>
                </div>
            </div>

            <div style="margin: 15px 0; padding: 10px; background: rgba(255,255,255,0.05); border-radius: 8px;">
                <div style="margin-bottom: 8px;">
                    <strong>Modification Rate:</strong> {stats['percentage_changed']:.1f}% modified, {stats['percentage_unchanged']:.1f}% preserved
                </div>
                <div style="margin-bottom: 8px;">
                    <span style="color: #90EE90;">✚ Added: {stats['added']} words</span> |
                    <span style="color: #FF4C4C;">✖ Removed: {stats['deleted']} words</span>
                </div>
            </div>
        """
        
        if stats['substitutions']:
            html += """
            <div style="margin-top: 15px; padding: 10px; background: rgba(255,255,255,0.05); border-radius: 8px;">
                <strong>🔄 Sample Word Substitutions:</strong>
                <div style="margin-top: 8px; font-size: 13px; line-height: 1.6;">
            """
            for orig, new in stats['substitutions']:
                html += (
                    f'<div style="margin: 4px 0;">'
                    f'<span style="color: #FF4C4C;">{orig}</span> → '
                    f'<span style="color: #90EE90;">{new}</span></div>'
                )
            html += """
                </div>
            </div>
            """
        
        html += """
            <div style="margin-top: 15px; padding: 8px; background: rgba(255,255,255,0.05); border-radius: 6px; font-size: 12px;">
                <strong>Legend:</strong>
                <span style="background-color: #FF4C4C; padding: 2px 6px; border-radius: 3px; margin: 0 4px;">Removed/Changed</span>
                <span style="background-color: #90EE90; padding: 2px 6px; border-radius: 3px; margin: 0 4px;">Added/New</span>
            </div>
        </div>
        """
        
        return html
    
    @staticmethod
    def format_quality_comparison(
        input_metrics: Dict,
        output_metrics: Dict
    ) -> str:
        """
        Format quality comparison between input and output
        
        Args:
            input_metrics: Quality metrics for input text
            output_metrics: Quality metrics for output text
            
        Returns:
            HTML string
        """
        def get_diff_color(val1, val2, inverse=False):
            """Helper to colorize improvement/decline"""
            if val1 == val2:
                return "white"
            better = val2 < val1 if inverse else val2 > val1
            return "#90ee90" if better else "#ff4c4c"
        
        # Calculate flow color (Higher is better)
        flow_color = get_diff_color(
            input_metrics['logical_flow'],
            output_metrics['logical_flow']
        )
        
        quality_html = f"""
        <div style="padding: 15px; background: #1a1a1a; border-radius: 10px; color: white; margin-top: 10px;">
            <h3 style="margin-top: 0; color: #add8e6; display: flex; align-items: center;">
                🛡️ Quality Comparison <span style="font-size: 0.7em; margin-left: 10px; opacity: 0.7;">(Input vs. Output)</span>
            </h3>
            <table style="width: 100%; text-align: left; border-collapse: separate; border-spacing: 0 8px;">
                <thead>
                    <tr style="color: #aaa; font-size: 0.9em; text-transform: uppercase;">
                        <th style="padding: 0 10px;">Metric</th>
                        <th style="padding: 0 10px;">Original</th>
                        <th style="padding: 0 10px;">Generated</th>
                    </tr>
                </thead>
                <tbody>
                    <tr style="background: rgba(255,255,255,0.05);">
                        <td style="padding: 10px; border-radius: 5px 0 0 5px;"><strong>📖 Readability</strong></td>
                        <td style="padding: 10px;">
                            {input_metrics['readability_score']:.1f} <br>
                            <span style="font-size: 0.8em; opacity: 0.7;">({input_metrics['readability_label']})</span>
                        </td>
                        <td style="padding: 10px; border-radius: 0 5px 5px 0;">
                            <strong>{output_metrics['readability_score']:.1f}</strong> <br>
                            <span style="font-size: 0.8em; color: #add8e6;">({output_metrics['readability_label']})</span>
                        </td>
                    </tr>
                    <tr style="background: rgba(255,255,255,0.05);">
                        <td style="padding: 10px; border-radius: 5px 0 0 5px;"><strong>🧠 Logical Flow</strong></td>
                        <td style="padding: 10px;">{input_metrics['logical_flow']:.2f}</td>
                        <td style="padding: 10px; border-radius: 0 5px 5px 0; color: {flow_color};">
                            <strong>{output_metrics['logical_flow']:.2f}</strong>
                        </td>
                    </tr>
                    <tr style="background: rgba(255,255,255,0.05);">
                        <td style="padding: 10px; border-radius: 5px 0 0 5px;"><strong>⚠️ Grammar Issues</strong></td>
                        <td style="padding: 10px;">{input_metrics['grammar_issues']}</td>
                        <td style="padding: 10px; border-radius: 0 5px 5px 0;">
                            <span style="color: {'#ff4c4c' if output_metrics['grammar_issues'] > input_metrics['grammar_issues'] else '#90ee90'}">
                                {output_metrics['grammar_issues']}
                            </span>
                        </td>
                    </tr>
                    <tr style="background: rgba(255,255,255,0.05);">
                        <td style="padding: 10px; border-radius: 5px 0 0 5px;"><strong>❗ Punctuation</strong></td>
                        <td style="padding: 10px;">{input_metrics['punctuation_issues']}</td>
                        <td style="padding: 10px; border-radius: 0 5px 5px 0;">
                            <span style="color: {'#ff4c4c' if output_metrics['punctuation_issues'] > input_metrics['punctuation_issues'] else '#90ee90'}">
                                {output_metrics['punctuation_issues']}
                            </span>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
        """
        
        return quality_html


