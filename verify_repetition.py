
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.quality.metrics import QualityMetrics

def test_repetition():
    print("Testing Anti-Echo Feature...")
    
    # Text with deliberate repetitions
    text = "The model is a good model because the model works well for the model task. Model performance is key for the model."
    
    print(f"\nAnalyzing text: '{text}'")
    
    try:
        metrics = QualityMetrics().calculate(text)
        repetition = metrics.get('repetition', {})
        
        print("\nResults:")
        print(f"Local Echo Score: {repetition.get('local_repetition_score')}")
        print(f"Total Repetitions: {repetition.get('total_repetitions_found')}")
        print("Top Global Repetitions:")
        for item in repetition.get('top_global_repetitions', []):
            print(f"  - {item['word']}: {item['count']} times")
            
        if repetition.get('total_repetitions_found', 0) > 0:
            print("\nSUCCESS: Repetitions detected!")
        else:
            print("\nFAILURE: No repetitions detected.")
            
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_repetition()
