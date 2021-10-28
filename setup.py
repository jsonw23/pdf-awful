from setuptools import setup

setup(name='pdfawful',
      version='0.1',
      description='Find and extract pdf attachments and pdf portfolios.',
      url='https://github.com/jasonw754/pdf-awful',
      author='Jason Williams',
      author_email='',
      license='MIT',
      packages=['pdfawful'],
      install_requires=[
        'PyPDF2'
      ],
      zip_safe=False)