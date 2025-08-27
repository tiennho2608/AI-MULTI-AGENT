import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from qa_service.evaluation import EvaluationSuite

def main():
    print("=== Technical Q&A Service Evaluation ===\n")
    
    evaluator = EvaluationSuite()
    results = evaluator.run_full_evaluation()
    
    print("\n=== Detailed Results ===")
    print(f"Overall Performance:")
    print(f"  - Hit@3 (Retrieval): {results['summary']['hit_at_3']:.1%}")
    print(f"  - Keyword Match Rate: {results['summary']['keyword_match_rate']:.1%}")  
    print(f"  - Tool Usage Accuracy: {results['summary']['tool_accuracy']:.1%}")
    
    print(f"\nRetrieval Analysis:")
    for detail in results['retrieval']['details']:
        status = "✓" if detail['hit'] else "✗"
        print(f"  {status} {detail['question'][:50]}... (score: {detail['top_score']:.3f})")

if __name__ == "__main__":
    main()