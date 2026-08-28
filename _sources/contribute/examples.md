---
title: "Creating Example Notebooks"
linkTitle: "Creating Examples"
weight: 1
aliases:
  - /tutorials/tutorial-template
  - /tutorials-examples/contribute/contribute-examples
description: >
  A brief guide for creating a new example notebooks.
---

# Creating Example Notebooks
We welcome example notebooks that demonstrate how to use tools within Neurodesk. These notebooks serve as valuable learning resources and promote reproducible workflows across the neuroimaging community.

Example notebooks are hosted in the <a href="https://github.com/neurodesk/neurodeskedu/tree/main/books/examples" target="_blank" rel="noopener">
  `neurodesk/neurodeskedu:examples`
</a> repository and are intended to be lightweight, self-contained, and easy to follow.


## Getting Started

To contribute a new notebook, follow the steps below:

### 1. Start from the template

Use the official <a href="https://github.com/neurodesk/neurodeskedu/tree/main/books/examples/template.ipynb" target="_blank" rel="noopener">
  example notebook template
</a> as a starting point. It includes guidance on formatting, structure, metadata, and citation instructions.

Each notebook should contain:

- A clear title and short description - aim for a short title that will fit in the left menu
- An overview of the tool or workflow demonstrated 
- The container/tool version used
- Code cells with explanatory comments
- Example data (or guidance on how to access it)

**Python packages** please consult the python packages included in the base image <a href="https://github.com/neurodesk/neurodesktop/blob/main/Dockerfile" target="_blank" rel="noopener">
  see list here
</a>. If you are using python packages different than these, be sure to `pip install` them in the workflow

### 2. Follow best practices

- Keep notebooks self-contained and executable top to bottom. Before being published, a Github Action will confirm the Notebook is working.
- Avoid hardcoded file paths where possible
- Use publicly accessible datasets
- Include inline comments and Markdown cells for explanation

For more detail, consult the <a href="https://github.com/neurodesk/neurodeskedu/blob/main/README.md" target="_blank" rel="noopener">
  README in the neurodeskedu repository
</a>.


---

## Saving and Submitting

1. Add your completed notebook to the appropriate folder under:

   <a href="https://github.com/neurodesk/neurodeskedu/tree/main/books/examples" target="_blank" rel="noopener">
  `/books/examples/`
</a>

2. Open a pull request in the <a href="https://github.com/neurodesk/neurodeskedu" target="_blank" rel="noopener">
  neurodeskedu repository
</a>

3. In your pull request, include:
   - A short description of your notebook
   - Any dependencies or expected output

4. Once your pull request is submitted, a GitHub Action will automatically run your notebook to confirm it executes successfully. Once the action passes and your pull request is merged, your notebook will be **published immediately** on the NeurodeskEDU site.

```{note}
By opening a pull request you agree to the [Terms of Submission](https://github.com/neurodesk/neurodeskedu/blob/main/TERMS_OF_SUBMISSION.md). 
```

## Review Process

Publishing and review are separate processes. Your notebook does not need to be reviewed before it is published — it goes live as soon as the automated checks pass and the pull request is merged. The review process happens afterwards to ensure quality and provide feedback.

Each notebook on the NeurodeskEDU site displays a review badge indicating its current review status:

- **Unreviewed** — the notebook has been published but has not yet been through peer review.
- **In Revision** — the notebook is currently being reviewed and may have changes requested.
- **Reviewed** — the notebook has passed peer review. The badge displays the name of the reviewer.

### How the review works

Reviews are managed via the <a href="https://github.com/neurodesk/neurodeskedu-reviews" target="_blank" rel="noopener">neurodeskedu-reviews</a> repository and take place publicly in GitHub issues and pull requests.

1. **A review issue is created** — your notebook is assigned a unique Review ID and queued for review.
2. **Reviewers are assigned** — one or more reviewers evaluate your notebook against the review checklist.
3. **Feedback is provided** — reviewers leave comments and suggestions directly on the pull request. We ask reviewers to complete their review within 2 weeks, and contributors to respond to feedback within 1 week.
4. **Revisions (if needed)** — address any requested changes and push updates. The badge will show **In Revision** during this stage.
5. **Acceptance** — once the reviewers are satisfied, the badge is updated to **Reviewed** with the reviewer's name.

### Review checklist

Reviewers evaluate submissions based on the following criteria:

- **License:** Does the notebook contain a LICENSE statement with a standard license (OSI-approved for code, Creative Commons for content)?
- **Authorship and date:** Are authors and date properly listed?
- **Citations and references:** Is the software properly cited? Do archival references include DOIs?
- **Format:** Does the notebook follow the NeurodeskEDU template?
- **Functionality:** Does the analysis run as outlined? Does it complete in a reasonable time?
- **Statement of need:** Is the purpose of the notebook clearly stated?
- **Dependencies:** Is there a clear list of dependencies, ideally with automated installation?
- **Learning objectives:** Are the learning objectives evident from the content and design?
- **Content scope:** Is the content substantial and appropriately scoped for the topic?
- **Explanations:** Are the analysis steps sufficiently documented?
- **Pedagogy:** Is the notebook easy to follow and mindful of cognitive load?
- **Content quality:** Is the writing concise and engaging? Is the code well crafted?

The full checklist is available in the <a href="https://github.com/neurodesk/neurodeskedu-reviews/blob/master/.buffy/templates/reviewer_checklist.md" target="_blank" rel="noopener">neurodeskedu-reviews repository</a>. For more details on the review process, including the conflict of interest policy, see the [Reviewing for NeurodeskEDU](review) page.

---

## Attribution

All notebooks contributors are acknowledged on the <a href="https://neurodesk.org/developers/contributors/" target="_blank" rel="noopener">
  Contributors page
</a>.  
To be listed, include your name and a short description in your pull request using <a href="https://github.com/neurodesk/neurodesk.github.io/blob/main/.github/content-templates/contributor-format.md" target="_blank" rel="noopener">
  this format
</a>.

---

## Need Help?

If you have questions or would like feedback before submitting:

- Open a [discussion](https://github.com/orgs/neurodesk/discussions)

We look forward to your contributions and thank you for supporting open and reproducible neuroimaging.
