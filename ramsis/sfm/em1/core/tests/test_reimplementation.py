"""
Test script used for regression testing of EM1 model
"""

import os
import pandas as pd
import unittest
from datetime import datetime, timedelta
from ramsis.sfm.em1.core import em1_model as e


# A stand alone test is recommended for the model itself,
# if the model code is kept in this repo.
# Some models are converted from other languages and forms,
# so at the very least a comparison test is required where
# outputs from both versions are compared.

dirpath = os.path.dirname(os.path.abspath(__file__))

###
# Insert test code
# transform data as the model_adaptor would, and call the
# required function in the model code.
# For a real test, see the EM1 implementation test of the same name.

###
# Test code
###


# Run test and test results against comparison files
class EM1Output(unittest.TestCase):

    def setUp(self):
        self.allowed_error = 1e-3
        self.comparison_n = open_comparison_data(
            "data/output.csv")
        a, b, mc, forecast_values = exec_forecast()
        self.output_a = a
        self.output_b = b
        self.output_mc = mc
        self.output_forecast_values = forecast_values

    def test_forecast(self):
        """Test the full model output."""
        diff = (self.comparison_n - self.output_forecast_values).abs()
        diff_truth = (diff < self.allowed_error).all()
        self.assertTrue(diff_truth.N)
        self.assertTrue(diff_truth.volume)

    def test_training_values(self):
        """Test the full model output."""
        self.assertTrue((self.output_a - 0.21982619) < self.allowed_error)
        self.assertTrue((self.output_b - 1.74624935) < self.allowed_error)
        self.assertTrue((self.output_mc - 0.8) < self.allowed_error)
