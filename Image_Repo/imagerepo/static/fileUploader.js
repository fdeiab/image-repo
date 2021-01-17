/* This function fetches the filename(s) 
   that the user selected and displays 
   the filename(s)
   https://stackoverflow.com/questions/26082721/how-to-display-selected-file-names-before-uploading-multiple-files-in-struts2/26101941
*/

getFilenames = function() {
    var input = document.getElementById('imgfile');
    var output = document.getElementById('filenamesList');
    var filenames = "";
    for (var i = 0; i < input.files.length; ++i) {
        filenames += '<li>' + input.files.item(i).name + '</li>';
    }
    output.innerHTML = '<ul>'+filenames+'</ul>';
}