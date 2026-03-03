import json
import jiwer
import pandas as pd
import matplotlib.pyplot as plt
import os
import glob

def calculate_wer(reference, hypothesis):
    """Calculate Word Error Rate (WER) using jiwer."""
    if not reference:
        return 1.0 if hypothesis else 0.0
    return jiwer.wer(reference, hypothesis)

def calculate_cer(reference, hypothesis):
    """Calculate Character Error Rate (CER) using jiwer."""
    if not reference:
        return 1.0 if hypothesis else 0.0
    return jiwer.cer(reference, hypothesis)

def analyze_fairness(json_path, output_prefix):
    """
    Perform fairness analysis on ASR model outputs.
    Calculates WER/CER per language and gender, and generates summary metrics and plots.
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    records = []
    for key, value in data.items():
        ref = value.get('true_transcription', '')
        hyp = value.get('pred_transcription', '')
        gender = value.get('gender', 'Unknown')
        language = value.get('true_language', 'Unknown')
        
        wer = calculate_wer(ref, hyp)
        cer = calculate_cer(ref, hyp)
        
        records.append({
            'gender': gender,
            'language': language,
            'wer': wer,
            'cer': cer
        })

    df = pd.DataFrame(records)
    
    # --- 1. Aggregated Gender Stats ---
    gender_stats = df.groupby('gender').agg({'wer': ['mean', 'count'], 'cer': 'mean'})
    gender_stats.columns = ['wer_mean', 'sample_count', 'cer_mean']
    
    # --- 2. Detailed Language-wise Stats per Gender ---
    lang_stats_overall = df.groupby('language').agg({'wer': 'mean', 'cer': 'mean'}).rename(columns={'wer': 'wer_mean', 'cer': 'cer_mean'})
    
    lang_gender_stats = df.groupby(['language', 'gender']).agg({
        'wer': ['mean', 'count'],
        'cer': 'mean'
    }).unstack()
    
    # Flatten multi-index columns for the detailed language-gender table
    new_columns = []
    for col in lang_gender_stats.columns:
        stat_type = col[0] # wer/cer
        measure = col[1]   # mean/count
        gender = col[2].lower() # male/female
        
        if measure == 'count':
            new_columns.append(f"{gender}_count")
        else:
            new_columns.append(f"{stat_type}_{gender}")
            
    lang_gender_stats.columns = new_columns
    
    # Combine overall language stats with gender-specific language stats
    final_lang_stats = lang_stats_overall.join(lang_gender_stats)
    
    # Select and order columns for final report
    desired_cols = ['wer_mean', 'wer_male', 'wer_female', 'male_count', 'female_count', 'cer_male', 'cer_female']
    final_lang_stats = final_lang_stats[[c for c in desired_cols if c in final_lang_stats.columns]]
    
    # --- 3. Fairness Metrics (Binary Gender) ---
    results = {}
    wer_male = gender_stats.loc['Male', 'wer_mean'] if 'Male' in gender_stats.index else None
    wer_female = gender_stats.loc['Female', 'wer_mean'] if 'Female' in gender_stats.index else None
    
    abs_wer_gap = 0
    if wer_male is not None and wer_female is not None:
        abs_wer_gap = abs(wer_male - wer_female)
        results['abs_wer_gap'] = abs_wer_gap

    if wer_male and wer_female and wer_male != 0:
        results['rel_wer_ratio'] = wer_female / wer_male

    results['worst_group_wer'] = gender_stats['wer_mean'].max()
    results['group_var'] = gender_stats['wer_mean'].var()
    results['max_min_disparity'] = gender_stats['wer_mean'].max() - gender_stats['wer_mean'].min()

    # --- 4. Visualizations ---
    # Metrics Bar Chart
    metrics_to_plot = {
        'Abs WER Gap': abs_wer_gap,
        'Max-Min Disp': results['max_min_disparity'],
        'Worst WER': results['worst_group_wer']
    }
    
    plt.figure(figsize=(10, 6))
    plt.bar(metrics_to_plot.keys(), metrics_to_plot.values(), color=['salmon', 'orange', 'red'])
    plt.title(f'Fairness Metrics - {os.path.basename(output_prefix)}')
    plt.ylabel('Value')
    plt.savefig(f"{output_prefix}_fairness_metrics.png")
    plt.close()

    # WER by Language and Gender Bar Chart
    lang_gender_wer_plot = df.groupby(['language', 'gender'])['wer'].mean().unstack()
    plt.figure(figsize=(14, 7))
    lang_gender_wer_plot.plot(kind='bar')
    plt.title(f'WER by Language and Gender - {os.path.basename(output_prefix)}')
    plt.ylabel('WER')
    plt.xlabel('Language')
    plt.legend(title='Gender')
    plt.tight_layout()
    plt.savefig(f"{output_prefix}_lang_gender_wer.png")
    plt.close()

    return results, final_lang_stats, gender_stats

if __name__ == "__main__":
    # Configuration
    json_dir = "Ethio-ASR/json_outputs/json_outputs_waxal/"
    output_dir = "fairness_results_waxal"
    os.makedirs(output_dir, exist_ok=True)
    
    json_files = glob.glob(os.path.join(json_dir, "*.json"))
    consolidated_excel = os.path.join(output_dir, "consolidated_waxal_fairness_analysis.xlsx")
    
    print(f"Starting fairness analysis for {len(json_files)} models...")
    
    with pd.ExcelWriter(consolidated_excel, engine='openpyxl') as writer:
        for json_file in json_files:
            model_name = os.path.basename(json_file).replace(".json", "").replace("-waxal", "")
            sheet_name = model_name[:31] # Excel sheet name limit
            
            print(f"  Processing {model_name}...")
            output_prefix = os.path.join(output_dir, f"{model_name}")
            
            _, detailed_stats, _ = analyze_fairness(json_file, output_prefix)
            detailed_stats.to_excel(writer, sheet_name=sheet_name)
            
    print(f"\nAnalysis complete. Consolidated report saved to: {consolidated_excel}")
