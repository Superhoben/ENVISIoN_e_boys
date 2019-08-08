const fs = require('fs')


var loadedDatasets = {};
var activeDatasetName;
var activeVisId;
//var loadedHdf5Files = [];
var tempHdf5Files = [];

var uiData;

// TODO: Validations for most text field inputs.
//       If they are empty you cant just send null


function sidebarLinkClicked() {
    if($(this).hasClass("subLink")){
        $("#sidebar a").not($(this).parent().parent().find("> li > a")).removeClass("active");
        $(this).parent().parent().find("> li > a").addClass("active")
    }
    else {
        $("#sidebar a").removeClass("active");
    }
    $(this).find("> a").addClass("active");
    
    var div = $($(this).data("show")).show();
    div.siblings("div").hide();
    console.log("sidebar link clicked")
}

function datasetFocused() {
    let name = $(this).find("> a")[0].textContent;
    console.log("dataset opened: ", name);
    datasetInfo = loadedDatasets[name];
    activeDatasetName = name;
}

function visualisationFocused() {
   activeVisId = $(this).data("vis-id");
   send_data("envision request", ["get_ui_data", activeVisId, []])
}

// --------------------------------
// ----- Dataset loader -----------
// --------------------------------

function loadDataset() {
    let isVaspPath = $("#vaspSourceCheckbox").is(":checked");
    let isHdf5Path = $("#hdf5SourceCheckbox").is(":checked");
    let datasetName = $("#datasetNameText").val()

    if (datasetName == "") {
        let idx = 1;
        while ("Dataset " + idx in loadedDatasets) idx++;
        datasetName = "Dataset " + idx;
    }

    let hdf5Path;

    if (isVaspPath) {
        let vaspPath = $("#vaspDirInput")[0].files[0].path;
        hdf5Path = "temp_" + tempHdf5Files.length + ".hdf5";
        tempHdf5Files.push(hdf5Path);
        console.log("Sending data?")
        send_data("parser request", ["All", hdf5Path, vaspPath]);
    }
    else if (isHdf5Path) {
        hdf5Path = $("#hdf5LoadInput")[0].files[0].path;
    }
    // add to list at bottom of page
    let elem = $(`
        <div class="row row-margin">
        <div class="input-group col">
        <div class="input-group-prepend medium">
        <label class="input-group-text">` + datasetName + `</label>
        </div>
        <input type="text" class="form-control" value="` + hdf5Path + `" disabled>
        <div class="input-group-append">
        <button class="btn btn-danger">Clear</button>
        </div>
        </div>
        </div>`);
    elem.find(".btn-danger").on("click", removeDataset);
    $("#datasetsList").append(elem);

    // add to sidebar
    let sidebarElem = $(`
        <div>
        <li data-show="#datasetPanel">
        <a href="#">` + datasetName + `</a>
        </li>
        <ul class="list-unstyled show">
        </ul>
        </div>`);
    sidebarElem.find("> li").on("click", sidebarLinkClicked);
    sidebarElem.find("> li").on("click", datasetFocused);
    $("#datasetLinks").append(sidebarElem);


    loadedDatasets[datasetName] = [hdf5Path, sidebarElem, elem, []];

    console.log(JSON.stringify(loadedDatasets));
}

function removeDataset() {
    let name = $(this).parent().parent().find(".input-group-prepend > label")[0].textContent;
    let datasetInfo = loadedDatasets[name];
    datasetInfo[1].remove();
    datasetInfo[2].remove();
    // TODO, remove path in dataset[0] if it was in tempHdf5Files
    // TODO, stop running visualisations using dataset
    for (var i = 0; i < datasetInfo[3].length; i++) {
        send_data("envision request", ["stop", datasetInfo[3][i], [false]]);
    }

    delete loadedDatasets[name];
    console.log("removing dataset: ", name);
    // $(this).parent().parent().parent().remove();
}

function startVisPressed() {
    let datasetInfo = loadedDatasets[activeDatasetName];
    let visTypes = ["charge","elf","parchg","unitcell","pcf","bandstructure","dos"];
    let selectionIndex = $("#visTypeSelection")[0].selectedIndex;
    let visType = visTypes[selectionIndex];
    let hdf5Path = datasetInfo[0];
    
    let visIndex = 0;
    while (datasetInfo[3].includes(activeDatasetName + "_" + visType + "_" + visIndex)) visIndex += 1;
    let visId = activeDatasetName + "_" + visType + "_" + visIndex;
    loadedDatasets[activeDatasetName][3].push(visId);

    // Add sidebar element
    let sidebarElem = $(`
        <li data-show="#visControlPanel" data-vis-id="` + visId + `" class="subLink">
        <a href="#">` + visType + "_" + visIndex + `<button class="btn btn-danger navbar-btn btn-sm float-right">Stop</button></a>
        </li>`);
    loadedDatasets[activeDatasetName][1].find("ul").append(sidebarElem);
    sidebarElem.on("click", sidebarLinkClicked);
    sidebarElem.on("click", visualisationFocused);

    // Start the visualisation
    send_data("envision request", ["start", visId, [visType, hdf5Path]]);
}

function stopVisPressed() {
    disableInputs();
    // send_data("envision request", ["toggle_tf_editor", activeVisId, [false]]);
    send_data("envision request", ["stop", activeVisId, [false]]);
}

function pathInputChanged() {
    let filePath = $(this)[0].files[0].path;
    $(this).next('.custom-file-label').addClass("selected").html(filePath);
}

function togglePathType() {
    let vaspDiv = $("#vaspSource")
    let hdf5Div = $("#hdf5Source")

    if ($("#vaspSourceCheckbox").is(":checked")) {
        vaspDiv.css("display", "block")
        hdf5Div.css("display", "none")
    }
    else if ($("#hdf5SourceCheckbox").is(":checked")) {
        vaspDiv.css("display", "none")
        hdf5Div.css("display", "block")
    }
}

function resetCanvasPositions() {
    let xPos = window.screenX + window.outerWidth;
    let yPos = window.screenY;
    send_data("envision request", ["position_canvases", activeVisId, [xPos, yPos]]);
    // send_data("envision request", ["toggle_tf_editor", activeVisId, [true]]);
}

function showVolumeDist() {
    send_data("envision request", ["show_volume_dist", activeVisId, []]);
}

// ----------------------------------
// ----- Volume rendering panel -----
// ----------------------------------

function bandChanged() {
    let selection = $("#bandSelection").val();
    send_data("envision request", ["set_active_band", activeVisId, [selection]]);

}

function shadingModeChanged() {
    let selectionIndex = $(this)[0].selectedIndex;
    send_data("envision request", ["set_shading_mode", activeVisId, [selectionIndex]]);
}

function volumeBackgroundChanged() {
    let color1 = hexToRGB($("#backgroundColor1").val());
    let color2 = hexToRGB($("#backgroundColor2").val());
    color1.push(1);
    color2.push(1);
    let styleIndex = $("#backgroundStyleSelection")[0].selectedIndex;
    console.log(JSON.stringify([color1, color2, styleIndex]));
    send_data("envision request", ["set_volume_background", activeVisId, [color1, color2, styleIndex]])
}

function updateMask() {
    if (!$("#transperancyCheckbox").is(':checked'))
        send_data("envision request", ["set_mask", activeVisId, [0, 1]]);
    else if (getTfPoints().length > 0)
        send_data("envision request", ["set_mask", activeVisId, [getTfPoints()[0][0], 1]]);
}

function addTfPointSubmitted() {
    let value = parseFloat($(this)[0][0].value);
    let alpha = parseFloat($(this)[0][1].value);
    let color = hexToRGB($(this)[0][2].value);
    color.push(alpha);

    send_data("envision request", ["add_tf_point", activeVisId, [value, color]]);
    visPanelChanged();
    return false;
}

function tfPointChanged() {
    send_data("envision request", ["set_tf_points", activeVisId, [getTfPoints()]]);
    visPanelChanged();
}

function removeTfPoint() {
    $(this).closest('[name="tfPoint"]').remove();
    send_data("envision request", ["set_tf_points", activeVisId, [getTfPoints()]]);
    updateMask();
    return false;
}

function sliceCanvasToggle() {
    send_data("envision request", ["toggle_slice_canvas", activeVisId, [$("#sliceCanvasCheck").is(":checked")]]);
    resetCanvasPositions();
}

function slicePlaneToggle() {
    send_data("envision request", ["toggle_slice_plane", activeVisId, [$("#slicePlaneCheck").is(":checked")]]);
}

function sliceHeightChanged() {
    let value = $(this).val();
    $("#sliceHeightRange").val(value);
    $("#sliceHeightText").val(value);
    if (value == "")
        value = 0.5;
    else
        value = parseFloat(value);
    send_data("envision request", ["set_plane_height", activeVisId, [value]]);
}

function sliceZoomChanged() {
    let value = $(this).val();
    $("#sliceZoomtRange").val(value);
    $("#sliceZoomText").val(value);
    let a = Math.pow(10.99, value) - 0.99;
    send_data("envision request", ["set_slice_zoom", activeVisId, [a]]);
}


function wrapModeSelected() {
    let selectedIndex = $("#sliceWrapSelection")[0].selectedIndex;
    let modeIndexes = [0, 2]
    send_data("envision request", ["set_texture_wrap_mode", activeVisId, [modeIndexes[selectedIndex]]]);
}

function sliceNormalChanged() {
    let x = parseFloat($(this)[0].children[1].value);
    let y = parseFloat($(this)[0].children[2].value);
    let z = parseFloat($(this)[0].children[3].value);
    send_data("envision request", ["set_plane_normal", activeVisId, [x, y, z]]);
    return false;
}

// --------------------------------
// ----- Partial charge panel -----
// --------------------------------

function partialBandAdded() {
    let band = $("#partialBandSelection").val();
    let mode = $("#partialModeSelection")[0].selectedIndex - 1;
    if (band == "band" || mode == -1)
        return false;
    band = parseInt(band);
    addPartialBandElement(band, mode);
    $("#partialBandSelection").val("band");
    $("#partialModeSelection").val("mode");
    send_data("envision request", ["select_bands", activeVisId, getPartialBandSelections()]);
    visPanelChanged();
    return false;
}

function partialBandChanged() {
    send_data("envision request", ["select_bands", activeVisId, getPartialBandSelections()]);
    visPanelChanged();
}

function partialBandRemoved() {
    $(this).remove();
    send_data("envision request", ["select_bands", activeVisId, getPartialBandSelections()]);
    return false;
}


// ---------------------------
// ----- 2-D graph panel -----
// ---------------------------

function xRangeSubmitted() {
    let min = parseFloat($("#xRangeMin").val());
    let max = parseFloat($("#xRangeMax").val());
    send_data("envision request", ["set_x_range", activeVisId, [min, max]]);
    visPanelChanged();
    return false;
}

function yRangeSubmitted() {
    // let min = $("#yRangeMin").val()!="" ? parseFloat($("#yRangeMin").val()) : -10000;
    let min = parseFloat($("#yRangeMin").val())
    let max = parseFloat($("#yRangeMax").val());
    send_data("envision request", ["set_y_range", activeVisId, [min, max]]);
    visPanelChanged();
    return false;
}

function verticalLineChecked() {
    let enable = $("#verticalLineCheck").is(":checked");
    send_data("envision request", ["toggle_vertical_line", activeVisId, [enable]]);
}

function verticalLineXSubmitted() {
    let value = parseFloat($("#verticalLineXInput").val());
    send_data("envision request", ["set_vertical_line_x", activeVisId, [value]]);
    return false;
}

function gridChecked() {
    let enable = $("#gridCheck").is(":checked");
    send_data("envision request", ["toggle_grid", activeVisId, [enable]]);
}

function gridSizeSubmitted() {
    let value = parseFloat($("#gridSizeInput").val());
    send_data("envision request", ["set_grid_size", activeVisId, [value]]);
    return false;
}

function xLabelChecked() {
    send_data("envision request", ["toggle_x_label", activeVisId, [$("#xLabelCheck").is(":checked")]]);
}

function yLabelChecked() {
    send_data("envision request", ["toggle_y_label", activeVisId, [$("#yLabelCheck").is(":checked")]]);
}

function nLabelsSubmitted() {
    let value = parseInt($("#labelCountInput").val());
    send_data("envision request", ["set_n_labels", activeVisId, [value]]);
    return false;
}

function ySelectionRadiosChanged() {
    if ($("#allYCheck").is(":checked")) {
        send_data("envision request", ["set_y_selection_type", activeVisId, [2]]);
        $("#specificY").hide();
        $("#multipleY").hide();
    }
    else if ($("#specificYCheck").is(":checked")) {
        send_data("envision request", ["set_y_selection_type", activeVisId, [0]]);
        $("#specificY").show();
        $("#multipleY").hide();
    }
    else if ($("#multipleYCheck").is(":checked")) {
        send_data("envision request", ["set_y_selection_type", activeVisId, [1]]);
        $("#specificY").hide();
        $("#multipleY").show();
    }
    // xRangeSubmitted();
    // yRangeSubmitted();
}

function ySingleSelectionChanged() {
    let selectionIndex = $("#ySingleSelection")[0].selectedIndex;
    send_data("envision request", ["set_y_single_selection_index", activeVisId, [selectionIndex]]);
}

function yMultiSelectionSubmitted() {
    let input = $("#yMultiSelectInput").val();
    send_data("envision request", ["set_y_multi_selection", activeVisId, [input]]);
    // xRangeSubmitted();
    // yRangeSubmitted();
    return false;
}

function hideAtomsChanged() {
    let enable = $("#hideAllAtomsCheck").is(":checked");
    if (!enable)
        send_data("envision request", ["hide_atoms", activeVisId, []]);
    else
        $('[name="atomRadiusSlider"]').trigger("input");
}

function atomRadiusChanged() {
    if (!$("#hideAllAtomsCheck").is(":checked"))
        return
    let value = parseInt($(this).val());
    let radius = (Math.pow(1.0243, value) - 1) / 12;
    let index = parseInt($(this).parent().parent().parent().index());
    send_data("envision request", ["set_atom_radius", activeVisId, [radius, index]]);
}

// ------------------------
// ----- Parser panel -----
// ------------------------

function parseClicked() {
    let vaspDir = $("#vaspDirInput")[0].files[0].path;
    let hdf5Dir = $("#hdf5DirInput")[0].files[0].path;
    let hdf5FileName = $("#hdf5FileNameInput").val();
    let parseType = $("#parseTypeSelect").val();

    if (!/^.*\.(hdf5|HDF5)$/.test(hdf5FileName)) {
        alert("File must end with .hdf5");
        return;
    }

    send_data("parser request", [[parseType], hdf5Dir + "/" + hdf5FileName, vaspDir])
    console.log(vaspDir, hdf5Dir, hdf5FileName, parseType);
}


// ----------------------------------
// ----- Python response events -----
// ----------------------------------

function uiDataRecieved(id, data) {
    console.log("UI data recieved")
    // TODO: Disable input elements by default, enable from here.
    if (id != activeVisId) {
        console.log("Data for inactive panel");
        return;
    }
    uiData = data;
    if (data[0] == "charge") {
        $("#visControlPanel").load("contentPanels/charge.html");
    } 
    // else if (id == "elf") {
    //     loadBands(data[0]);
    //     loadAtoms(data[1]);
    //     loadTFPoints(data[2]);
    // } else if (id == "parchg") {
    //     loadAvailablePartials(data[0])
    //     loadActivePartials(data[1]);
    //     loadAtoms(data[2]);
    //     loadTFPoints(data[3]);
    // } else if (id = "bandstructure") {
    //     loadXRange(data[0]);
    //     loadYRange(data[1]);
    //     loadLabelCount(data[2]);
    //     loadAvailableDatasets(data[3]);
    // } else if (id == "pcf") {
    //     loadXRange(data[0]);
    //     loadYRange(data[1]);
    //     loadLabelCount(data[2]);
    //     loadAvailableDatasets(data[3]);
    // } else if (id == "dos") {
    //     loadXRange(data[0]);
    //     loadYRange(data[1]);
    //     loadLabelCount(data[2]);
    //     loadAvailableDatasets(data[3]);
    // }
    // enableInputs();
}


// ---------------------------------------
// ----- Interface loading functions -----
// ---------------------------------------

function loadBands(bands) {
    console.log(bands);
    $("#bandSelection").empty();
    for (let i = 0; i < bands.length; i++) {
        if (i == bands.length - 1)
            $("#bandSelection").append("<option selected>" + bands[i] + "</option>")
        else
            $("#bandSelection").append("<option>" + bands[i] + "</option>")
    }
}

function loadAtoms(atoms) {
    $("#atomControls").empty();
    for (let i = 0; i < atoms.length; i++) {
        let atomControlElement = $(
            '<div class="form-row row-margin" name="atomControlRow">' +
            '<div class="col-sm-3">' +
            // '<div class="form-check">' +
            // '<input type="checkbox" class="form-check-input" checked>' +
            '<label class="form-check-label">' + atoms[i] + ' radius</label>' +
            // '</div>' +
            '</div>' +
            '<div class="col-sm-4">' +
            '<div class="form-group">' +
            '<input type="range" class="form-control-range" name="atomRadiusSlider">' +
            '</div>' +
            '</div>' +
            '</div>')
        $("#atomControls").append(atomControlElement)
        atomControlElement.find(".form-control-range").on("input", atomRadiusChanged)
    }
}

function loadTFPoints(points) {
    $("#tfPoints").empty();
    for (let i = 0; i < points.length; i++) {
        console.log("POINT ADDED")
        let hexColor = rgbToHex(points[i][1][0], points[i][1][1], points[i][1][2])
        addTfPointElement(points[i][0], Math.round(points[i][1][3] * 1000000) / 1000000, hexColor)
    }
    updateMask();
}

function loadAvailableDatasets(options) {
    $("#possibleYDatasets").empty();
    $("#ySingleSelection").empty();
    for (let i = 0; i < options.length; i++) {
        $("#possibleYDatasets").append("<option>[" + i + "]: " + options[i] + "</option>");
        $("#ySingleSelection").append("<option>" + options[i] + "</option>");
    }
    $("#ySingleSelection > option")[1].selected = true;
}

function loadAvailablePartials(options) {
    $("#partialBandSelection > option").slice(1).remove();
    $("#partialModeSelection > option").slice(1).remove();
    for (let i = 0; i < options[0].length; i++)
        $("#partialBandSelection").append("<option>" + options[0][i] + "</option>");
    for (let i = 0; i < options[1].length; i++)
        $("#partialModeSelection").append("<option>" + options[1][i] + "</option>");
}

function loadActivePartials(partials) {
    $("#partialBands").empty();
    for (let i = 0; i < partials[0].length; i++) {
        addPartialBandElement(partials[0][i], partials[1][i]);
    }
}

function loadXRange(range) {
    $("#xRangeMin").val(range[1]);
    $("#xRangeMax").val(range[0]);
}

function loadYRange(range) {
    $("#yRangeMin").val(range[1]);
    $("#yRangeMax").val(range[0]);
}

function loadLabelCount(n) {
    $("#labelCountInput").val(n);
}

// -----------------------------------
// ----- Interface value reading -----
// -----------------------------------

function getXRange() {

}

function getTfPoints() {
    // Return a list containing current tfPonts
    let tfPoints = [];
    for (let i = 0; i < $("#tfPoints")[0].children.length; i++) {
        let formNode = $("#tfPoints")[0].children[i].children[0];
        if (formNode.getAttribute("id") == "tfAdder")
            continue;
        let value = parseFloat(formNode.children[0].children[0].value);
        let alpha = parseFloat(formNode.children[0].children[1].value);
        let color = hexToRGB(formNode.children[0].children[2].value);
        color.push(alpha);
        tfPoints.push([value, color]);
    }
    return tfPoints;
}

function addTfPointElement(value, alpha, color) {
    // Adds an elemend representing the point to the list in the interface.
    let points = getTfPoints();
    if (points.find(function (point) { return point[0] == value }) != undefined) {
        console.log("Point with value already already exist.");
        return false
    }

    let pointElement = $(
        '<div class="row row-margin" name="tfPoint">' +
        '<div class="col-sm-10">' +
        '<div class="input-group">' +
        '<input type="text" class="form-control" value="' + value + '">' +
        '<input type="text" class="form-control" value="' + alpha + '">' +
        '<input class="form-control" type="color" value="' + color + '">' +
        '<div class="input-group-append">' +
        '<button class="btn btn-primary" type="submit">-</button>' +
        '</div>' +
        '</div>' +
        '</div>' +
        '</div>');

    let insertionIndex = points.findIndex(function (point) { return point[0] > value });
    if (insertionIndex == -1)
        $("#tfPoints").append(pointElement);
    else {
        pointElement.insertBefore($("#tfPoints")[0].children[insertionIndex])
    }
    pointElement.find("button").on("click", removeTfPoint);
    pointElement.find("input").on("change", tfPointChanged);
}

function addPartialBandElement(band, mode) {
    let elem = $(`
    <form class="row row-margin">
      <div class="input-group col-sm-10">
        <div class="input-group-prepend medium">
          <label class="input-group-text">Active band</label>
        </div>
        <select class="custom-select" name="bandSelect">
        </select>
        <select class="custom-select" name="modeSelect">
        </select>
        <div class="input-group-append">
          <button class="btn btn-primary" type="submit">&nbsp;-</button>
        </div>
      </div>
    </form>`);

    // Copy options from the original element, excluding first option.
    elem.find('[name="bandSelect"]').append($("#partialBandSelection > option").clone().slice(1));
    elem.find('[name="modeSelect"]').append($("#partialModeSelection > option").clone().slice(1));

    // Set correct selected option.
    elem.find('[name="bandSelect"]').val(band);
    elem.find('[name="modeSelect"]')[0][mode].selected = true;

    elem.on("submit", partialBandRemoved)
    elem.find('[name="bandSelect"],[name="modeSelect"]').on("change", partialBandChanged);
    $("#partialBands").append(elem);
}

function getPartialBandSelections() {
    // Return two lists containing active bands and corresponding modes
    let bands = [];
    let modes = [];
    for (let i = 0; i < $("#partialBands")[0].children.length; i++) {
        let inputGroup = $("#partialBands")[0].children[i].children[0];
        let band = parseInt(inputGroup.children[1].value);
        let mode = inputGroup.children[2].selectedIndex
        bands.push(band)
        modes.push(mode)
    }
    return [bands, modes];
}

// ---------------------------------
// ----- Panel initializations -----
// ---------------------------------

function visPanelChanged() {
    console.log("Updating panel: ", activeVisId);
    send_data("envision request", ["get_ui_data", activeVisId, []]);
}

function disableInputs() {
    $("#visSettings :input").attr("disabled", true);
    $("#visSettings :button").attr("disabled", true);
    // $("#visSettings > select").attr("disabled", true);
    // $("#visSettings > submit").attr("disabled", true);
}

function enableInputs() {
    $("#visSettings :input").attr("disabled", false);
    $("#visSettings :button").attr("disabled", false);
    // $("#visSettings :select").attr("disabled", false);
    // $("#visSettings :submit").attr("disabled", false);
}
// function initializeChargePanel() {
//     console.log("CHG")
//     // $("#visSettings :input").attr("disabled", false);
//     send_data("envision request", ["get_ui_data", "charge", []])
//     // send_data("envision request", ["get_bands", "charge", []])
//     // send_data("envision request", ["get_atom_names", "charge", []])
//     // send_data("envision request", ["get_tf_points", "charge", []])
// }

// function initializeELFPanel() {
//     console.log("ELF")
//     // $("#visSettings :input").attr("disabled", false);
//     send_data("envision request", ["get_ui_data", "elf", []])
//     // send_data("envision request", ["get_bands", "elf", []])
//     // send_data("envision request", ["get_atom_names", "elf", []])
//     // send_data("envision request", ["get_tf_points", "elf", []])
// }

// function initializeParchgPanel() {
//     console.log("Parchg")
//     send_data("envision request", ["select_bands", "parchg", [[0, 1], [0, 1]]])
//     // $("#visSettings :input").attr("disabled", false);
//     // send_data("envision request", ["get_bands", "elf", []])
//     // send_data("envision request", ["get_atom_names", "elf", []])
//     // send_data("envision request", ["get_tf_points", "elf", []])
// }

// function initializeBandstructurePanel() {
//     console.log("Bandstructure")
//     send_data("envision request", ["get_available_datasets", "bandstructure", []])
// }

// function initializePCFPanel(){
//     console.log("PCF")
//     send_data("envision request", ["get_available_datasets", "pcf", []])
// }

// function initializeDOSPanel(){
//     console.log("PCF")
//     send_data("envision request", ["get_available_datasets", "dos", []])
// }