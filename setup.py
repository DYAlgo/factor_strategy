from setuptools import setup

setup(
    name="factor_strategy",
    version = "0.1",
    requires = ['numpy', 'scikit-learn', 'pandas', 'pyfolio', 'alphalens'],
    author="Darren Y",
    description="Factor investing modelling project",
)
