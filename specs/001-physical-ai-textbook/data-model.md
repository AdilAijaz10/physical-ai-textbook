# Data Model: Physical AI & Humanoid Robotics Textbook

## Textbook Content
- **Fields**:
  - id (string): unique identifier
  - title (string): content title
  - body (string): content in MDX format
  - module (string): associated module
  - week (integer): associated week number
  - learningObjectives (array): list of learning objectives
  - prerequisites (array): required knowledge before reading
  - codeExamples (array): embedded code examples
  - exercises (array): practical exercises
  - diagrams (array): visual aids
  - createdAt (datetime): creation timestamp
  - updatedAt (datetime): last modification timestamp
- **Relationships**: Contains Modules, Weekly Content, Code Examples, Practical Exercises
- **Validation**: Title and body are required, week must be between 1-13

## Module
- **Fields**:
  - id (string): unique identifier
  - title (string): module title (e.g., "The Robotic Nervous System")
  - description (string): module overview
  - weeks (array): associated weeks
  - learningObjectives (array): overall module objectives
  - order (integer): sequence order (1-4)
  - createdAt (datetime): creation timestamp
  - updatedAt (datetime): last modification timestamp
- **Relationships**: Contains multiple Weekly Content items
- **Validation**: Title and description are required, order must be between 1-4

## Weekly Content
- **Fields**:
  - id (string): unique identifier
  - title (string): weekly content title
  - description (string): weekly overview
  - module (string): parent module ID
  - weekNumber (integer): week number (1-13)
  - content (array): content sections
  - learningObjectives (array): weekly objectives
  - codeExamples (array): weekly code examples
  - exercises (array): weekly exercises
  - createdAt (datetime): creation timestamp
  - updatedAt (datetime): last modification timestamp
- **Relationships**: Belongs to Module, contains Code Examples, Practical Exercises
- **Validation**: Title and weekNumber are required, weekNumber must be between 1-13

## Code Example
- **Fields**:
  - id (string): unique identifier
  - title (string): example title
  - description (string): explanation of the example
  - code (string): the actual code snippet
  - language (string): programming language (e.g., Python, C++)
  - associatedContent (string): parent content ID
  - explanation (string): step-by-step explanation
  - runnable (boolean): whether example can be run independently
  - createdAt (datetime): creation timestamp
  - updatedAt (datetime): last modification timestamp
- **Relationships**: Belongs to Textbook Content
- **Validation**: Title, code, and language are required

## Practical Exercise
- **Fields**:
  - id (string): unique identifier
  - title (string): exercise title
  - description (string): detailed exercise description
  - difficulty (string): difficulty level (beginner, intermediate, advanced)
  - associatedContent (string): parent content ID
  - instructions (string): step-by-step instructions
  - expectedOutcome (string): what students should achieve
  - resources (array): additional resources needed
  - createdAt (datetime): creation timestamp
  - updatedAt (datetime): last modification timestamp
- **Relationships**: Belongs to Textbook Content
- **Validation**: Title, description, and instructions are required

## Hardware Requirements
- **Fields**:
  - id (string): unique identifier
  - title (string): requirements category title
  - description (string): detailed requirements description
  - minimumSpecs (object): minimum system specifications
  - recommendedSpecs (object): recommended system specifications
  - setupInstructions (string): step-by-step setup guide
  - compatibilityNotes (string): notes about compatibility
  - createdAt (datetime): creation timestamp
  - updatedAt (datetime): last modification timestamp
- **Relationships**: Referenced by Textbook Content
- **Validation**: Title and description are required

## Learning Objective
- **Fields**:
  - id (string): unique identifier
  - title (string): objective statement
  - description (string): detailed explanation of the objective
  - associatedModule (string): parent module ID (optional)
  - associatedWeek (string): parent week ID (optional)
  - associatedContent (string): parent content ID (optional)
  - measurable (boolean): whether objective is measurable
  - createdAt (datetime): creation timestamp
  - updatedAt (datetime): last modification timestamp
- **Relationships**: Belongs to Module, Weekly Content, or Textbook Content
- **Validation**: Title is required

## Glossary Term
- **Fields**:
  - id (string): unique identifier
  - term (string): the term being defined
  - definition (string): clear definition of the term
  - category (string): category (e.g., robotics, AI, programming)
  - examples (array): usage examples
  - relatedTerms (array): related glossary term IDs
  - createdAt (datetime): creation timestamp
  - updatedAt (datetime): last modification timestamp
- **Relationships**: Referenced by Textbook Content
- **Validation**: Term and definition are required