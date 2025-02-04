# PDF Manager

PDF Manager is a graphical user interface (GUI) application built with PyQt5 for managing PDF files. It allows you to perform various operations such as adding, renaming, merging, inserting pages, deleting pages, and creating new PDFs. Additionally, it supports the manipulation of images by converting them into PDF format and editing pages in existing PDFs.

## Features

* **Add PDF files** : Add single or multiple PDF files to the application.
* **Bulk Rename** : Rename multiple PDFs according to a specified pattern.
* **Merge PDFs** : Merge selected PDFs into one.
* **Insert Pages** : Insert pages from another PDF or image into an existing PDF.
* **Delete Pages** : Select and delete specific pages from a PDF.
* **Crop Images** : Crop images before converting them into PDFs.
* **Preview Pages** : View thumbnails of pages in a PDF file and preview a larger image of the selected page.
* **Create New PDF** : Generate a new PDF with a specified number of blank pages.
* **File Management** : Manage the PDFs, including adding, renaming, and removing files.

## Requirements

* Python 3.x
* PyQt5
* PyPDF2
* ReportLab
* Fitz (PyMuPDF)

## Installation

To install the required dependencies, run:

<pre class="!overflow-visible"><div class="contain-inline-size rounded-md border-[0.5px] border-token-border-medium relative bg-token-sidebar-surface-primary dark:bg-gray-950"><div class="flex items-center text-token-text-secondary px-4 py-2 text-xs font-sans justify-between rounded-t-md h-9 bg-token-sidebar-surface-primary dark:bg-token-main-surface-secondary select-none">bash</div><div class="sticky top-9 md:top-[5.75rem]"><div class="absolute bottom-0 right-2 flex h-9 items-center"><div class="flex items-center rounded bg-token-sidebar-surface-primary px-2 font-sans text-xs text-token-text-secondary dark:bg-token-main-surface-secondary"><span class="" data-state="closed"><button class="flex gap-1 items-center select-none px-4 py-1" aria-label="Zkopírovat"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="icon-xs"><path fill-rule="evenodd" clip-rule="evenodd" d="M7 5C7 3.34315 8.34315 2 10 2H19C20.6569 2 22 3.34315 22 5V14C22 15.6569 20.6569 17 19 17H17V19C17 20.6569 15.6569 22 14 22H5C3.34315 22 2 20.6569 2 19V10C2 8.34315 3.34315 7 5 7H7V5ZM9 7H14C15.6569 7 17 8.34315 17 10V15H19C19.5523 15 20 14.5523 20 14V5C20 4.44772 19.5523 4 19 4H10C9.44772 4 9 4.44772 9 5V7ZM5 9C4.44772 9 4 9.44772 4 10V19C4 19.5523 4.44772 20 5 20H14C14.5523 20 15 19.5523 15 19V10C15 9.44772 14.5523 9 14 9H5Z" fill="currentColor"></path></svg>Zkopírovat</button></span></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="!whitespace-pre language-bash"><span>pip install pyqt5 pypdf2 reportlab PyMuPDF
</span></code></div></div></pre>

## Running the Application

To run the application, execute the following command:

<pre class="!overflow-visible"><div class="contain-inline-size rounded-md border-[0.5px] border-token-border-medium relative bg-token-sidebar-surface-primary dark:bg-gray-950"><div class="flex items-center text-token-text-secondary px-4 py-2 text-xs font-sans justify-between rounded-t-md h-9 bg-token-sidebar-surface-primary dark:bg-token-main-surface-secondary select-none">bash</div><div class="sticky top-9 md:top-[5.75rem]"><div class="absolute bottom-0 right-2 flex h-9 items-center"><div class="flex items-center rounded bg-token-sidebar-surface-primary px-2 font-sans text-xs text-token-text-secondary dark:bg-token-main-surface-secondary"><span class="" data-state="closed"><button class="flex gap-1 items-center select-none px-4 py-1" aria-label="Zkopírovat"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="icon-xs"><path fill-rule="evenodd" clip-rule="evenodd" d="M7 5C7 3.34315 8.34315 2 10 2H19C20.6569 2 22 3.34315 22 5V14C22 15.6569 20.6569 17 19 17H17V19C17 20.6569 15.6569 22 14 22H5C3.34315 22 2 20.6569 2 19V10C2 8.34315 3.34315 7 5 7H7V5ZM9 7H14C15.6569 7 17 8.34315 17 10V15H19C19.5523 15 20 14.5523 20 14V5C20 4.44772 19.5523 4 19 4H10C9.44772 4 9 4.44772 9 5V7ZM5 9C4.44772 9 4 9.44772 4 10V19C4 19.5523 4.44772 20 5 20H14C14.5523 20 15 19.5523 15 19V10C15 9.44772 14.5523 9 14 9H5Z" fill="currentColor"></path></svg>Zkopírovat</button></span></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="!whitespace-pre language-bash"><span>python editor.py
</span></code></div></div></pre>

This will launch the PDF Manager window, where you can start managing your PDF files.

## Components and Functionality

### 1. **BulkRenameDialog.py**

This dialog allows you to bulk rename PDF files based on a given pattern. You can specify the old pattern and the new pattern to replace within the file names.

### 2. **ImageCropDialog.py**

This dialog enables cropping of an image before it is added as a page to a PDF. The image is displayed in a `QGraphicsView`, and users can select the area to crop using a rubber band.

### 3. **InsertPagesDialog.py**

This dialog allows you to insert pages from another PDF or an image into an existing PDF. You can choose the page number to insert before and the type of file (PDF or image).

### 4. **MergePDFDialog.py**

This dialog lets you merge multiple PDF files by selecting their order and specifying an output path.

### 5. **editor.py**

This is the main application file. It provides the user interface to interact with all the dialogs and functionalities such as adding PDFs, renaming files, merging PDFs, inserting pages, deleting pages, and more.

### Dialog Descriptions:

* **Bulk Rename** : Lets you rename multiple PDFs in bulk based on a pattern.
* **Image Crop** : Crop and adjust images before converting them to PDF.
* **Insert Pages** : Insert PDF or image pages into another PDF.
* **Merge PDFs** : Merge multiple PDF files into one.

### Key Classes and Their Purpose:

* **`PDFManagerWindow`** : This is the main window of the application that manages the user interface. It handles PDF file management, including adding, renaming, deleting, and merging PDFs.
* **`BulkRenameDialog`** : A dialog for renaming PDF files in bulk according to a given pattern.
* **`InsertPagesDialog`** : A dialog for selecting and inserting pages from other files into the current PDF.
* **`MergePDFDialog`** : A dialog to handle the merging of multiple PDF files.

## How to Use:

1. **Adding PDFs** :

* Click the "Add PDF" button to select and add a PDF file.
* Alternatively, you can add multiple PDFs by selecting them in the "Add More PDFs" dialog.

1. **Renaming PDFs** :

* Click "Bulk Rename" and enter the pattern you want to replace in the filenames.

1. **Merging PDFs** :

* Select multiple PDF files, click "Merge PDFs," and arrange the files in the desired order.
* Choose an output path for the merged PDF.

1. **Inserting Pages** :

* Select a PDF file and click "Insert Pages" to insert pages from another PDF or an image into the selected file.

1. **Deleting Pages** :

* Select pages to delete and click "Apply Deletions."

1. **Creating a New PDF** :

* Click "Create New PDF" to generate a new PDF with a specified number of blank pages.

1. **Saving PDFs** :

* PDFs are automatically saved when edits are made, or you can use the "Save" button to overwrite the original file.

## License

This project is licensed under the MIT License - see the [LICENSE]() file for details.

---

### Functionality Breakdown

 **BulkRenameDialog** :
Allows users to enter a "pattern" to match in filenames and a "new pattern" to rename files accordingly.

* `get_rename_params()`: Returns the old pattern and new pattern entered by the user.

 **ImageCropDialog** :
Used to crop images before converting them into PDFs.

* `getCroppedPixmap()`: Returns the cropped image as a QPixmap object.

 **InsertPagesDialog** :
Lets the user choose a file to insert into an existing PDF and specifies the page number before which the new pages should be inserted.

* `get_insert_params()`: Returns the selected file path, page number, and insert type (PDF or image).

 **MergePDFDialog** :
Allows users to select multiple PDFs, set their order, and specify an output file path.

* `get_file_order()`: Returns the order of files selected for merging.
* `get_output_path()`: Returns the output path where the merged PDF will be saved.
