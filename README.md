# Confidential ML Utilities

[![python](https://github.com/Azure/confidential-ml-utils/workflows/python/badge.svg)](https://github.com/Azure/confidential-ml-utils/actions?query=workflow%3Apython)
[![CodeQL](https://github.com/Azure/confidential-ml-utils/workflows/CodeQL/badge.svg)](https://github.com/Azure/confidential-ml-utils/actions?query=workflow%3ACodeQL)
[![PyPI version](https://badge.fury.io/py/confidential-ml-utils.svg)](https://badge.fury.io/py/confidential-ml-utils)
[![Python versions](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/confidential-ml-utils)](https://pypi.org/project/confidential-ml-utils/)

Confidential ML is the practice of training machine learning models without
seeing the training data. It is needed in many enterprises to satisfy the
strict compliance and privacy guarantees they provide to their customers. This
repository contains a set of utilities for confidential ML, with a special
emphasis on using PyTorch in
[Azure Machine Learning pipelines](https://aka.ms/pl-concept)
([getting started](https://docs.microsoft.com/en-us/azure/machine-learning/tutorial-1st-experiment-sdk-setup-local))
 
## Using

Compliant logging library see:
[docs/logging](https://github.com/Azure/confidential-ml-utils/blob/master/docs/logging/README.md)

VS Code Snippets see:
[docs/snippets](https://github.com/Azure/confidential-ml-utils/blob/master/docs/snippets/README.md)

## Contributing

This project welcomes contributions and suggestions. Most contributions require
you to agree to a Contributor License Agreement (CLA) declaring that you have
the right to, and actually do, grant us the rights to use your contribution.
For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether
you need to provide a CLA and decorate the PR appropriately (e.g., status check,
comment). Simply follow the instructions provided by the bot. You will only need
to do this once across all repos using our CLA.

This project has adopted the
[Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the
[Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any
additional questions or comments.
