"""
Self-contained test script for running the structural transformation model.
"""
import os
import sys
import importlib.util

def load_module(file_path, module_name):
    """Dynamically load a module from file path"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

def main():
    """Run a test of the structural transformation model with real data"""
    print("Testing Structural Transformation Model with real trade data")
    print("-" * 70)
    
    # Define paths
    project_root = os.path.dirname(os.path.abspath(__file__))
    structural_model_path = os.path.join(project_root, 'models', 'structural_transformation.py')
    
    # Load the structural transformation module
    try:
        st_module = load_module(structural_model_path, 'structural_transformation')
        StructuralTransformationModel = st_module.StructuralTransformationModel
        print("Successfully loaded structural transformation model")
    except Exception as e:
        print(f"Error loading structural transformation model: {e}")
        return
    
    # Create config
    config = {
        'data_path': os.path.join(project_root, 'data', 'bd_trade_data.csv'),
    }
    
    # Initialize model
    try:
        model = StructuralTransformationModel(config)
        print("Successfully initialized model")
    except Exception as e:
        print(f"Error initializing model: {e}")
        return
    
    # Test for multiple years
    test_years = [2023, 2022, 2021]
    
    for year in test_years:
        print("\n" + "=" * 50)
        print(f"SIMULATING YEAR {year}")
        print("=" * 50)
        
        # Run simulation for this year
        try:
            results = model.simulate_step(year)
            
            # Display results
            print("\nSummary of Results:")
            print(f"Export Diversification HHI: {results['export_diversity_hhi']:.4f}")
            print(f"Capability Index: {results['capability_index']:.4f}")
            print(f"Industrial Policy Effectiveness: {results['industrial_policy_effectiveness']:.4f}")
            
            print("\nExport Values by Sector (billion USD):")
            for sector, value in sorted(results['export_sectors'].items(), key=lambda x: x[1], reverse=True):
                print(f"  - {sector}: ${value:.3f} billion")
        except Exception as e:
            print(f"Error simulating year {year}: {e}")

if __name__ == "__main__":
    main()
