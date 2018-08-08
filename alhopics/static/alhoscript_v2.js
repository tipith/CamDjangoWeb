  var static_loc = "../static/"
  var epochs = {
        current: -1,
        order: []
    };

  function anim_image(epoch)
  {
    if (epoch in epochs)
    {
      curr_selection = document.getElementById("cam_txt_" + epochs.current)
      if (curr_selection)
        curr_selection.style.color = '#0000ff';
      epochs.current = epoch;
      document.getElementById("cam_txt_" + epochs.current).style.color = '#ff0000';

      for (pic of epochs[epoch])
      {
        document.getElementById("cam" + pic.idcamera + "_image").src = pic.preload_img.src;
      }
    }
  }

  function updateLightControl()
  {
    $.ajax({
      type: "GET",
      url: "api/events",
      data: { format: 'json', type: "light" },
      success: function(response)
      {
        console.log("update light events response: " + response);
        buildHtmlTable(response, "#lightcontrol");
      }
    });
  }

  function updateMovement()
  {
    $.ajax({
      type: "GET",
      url: "api/events",
      data: { format: 'json', type: "movement" },
      success: function(response)
      {
        console.log("update movement events response: " + response);
        buildHtmlTable(response, "#movement");
      }
    });
  }

  function sendCommand(command, state)
  {
    $.ajax(
    {
      type: "GET",
      url: "api/command",
      data: { format: 'json', command: command, state: state },
      success: function(response)
      {
        console.log("command response: " + response);
      }
    });
  }

  function updateDates(_date, _dir, _type)
  {
    for (const cam_id of cam_ids)
    {
        $.ajax({
          type: "GET",
          url: "api/statistics",
          data: { format: 'json', camera: cam_id, type: _type },
          success: function(response)
          {
            document.getElementById("cam" + cam_id + "_info3").innerHTML = "Data <b>" + response.data_month + "</b> Mt (kk), <b>" + response.data_day + "</b> Mt (vrk)";
            document.getElementById("cam" + cam_id + "_info4").innerHTML = "Kuvia <b>" + response.pics_month + "</b> (kk), <b>" + response.pics_day + "</b> (vrk)";
          }
        });

        $.getJSON(static_loc + "data/vars.json", function(data)
        {
          days = Math.floor(data["cam" + cam_id].uptime / 86400);
          hours = Math.floor((data["cam" + cam_id].uptime % 86400) / 3600);
          document.getElementById("cam" + cam_id + "_info1").innerHTML = "Käynnissä <b>" + days + "</b> päivää, <b>" + hours + "</b> tuntia";
          document.getElementById("cam" + cam_id + "_info2").innerHTML = "Viimeisin <b>" + data["cam" + cam_id].last_heard + "</b>";
        });
    }

    $.ajax({
      type: "GET",
      url: "api/pictures",
      data: { format: 'json', date: _date.toISOString(), dir: _dir, type: _type, count: 64 },
      success: function(response)
      {
        addImages(response);
      }
    });
  }

  function addZero(i)
  {
    if (i < 10) {
        i = "0" + i;
    }
    return i;
  }

  function scroll_image(e)
  {
	var delta = Math.max(-1, Math.min(1, (e.wheelDelta || -e.detail)));
	var idx = epochs.order.indexOf(epochs.current);
	if (idx >= 0)
	{
	  if (idx == 0 && delta == 1) {
	    getPreviousImages();
	  } else if (idx == (epochs.order.length - 1) && delta == -1) {
	    getNextImages();
	  } else {
	    anim_image(epochs.order[idx - delta]);
	  }
	}

    e.preventDefault();
  }

  function roundTimestampToEpoch(timestamp)
  {
    var coeff = 1000 * 60 * 5;
    var date = new Date(timestamp);
    return new Date(Math.round(date.getTime() / coeff) * coeff).getTime();
  }

  function addImages(_images)
  {
    var old_tbody = document.getElementById("cam_select").tBodies[0];
    var new_tbody = document.createElement('tbody');

    if (new_tbody.addEventListener) {
        new_tbody.addEventListener("mousewheel", scroll_image, false);  // IE9, Chrome, Safari, Opera
        new_tbody.addEventListener("DOMMouseScroll", scroll_image, false);  // Firefox
    }

    // remove preloads
    //for (const e of epochs.order)
    //{
    //    for (let pic of e)
    //    {
    //        pic.preload_img.src = ""
    //    }
    //}

    epochs = {
        current: -1,
        order: []
    };

    for (let pic of _images)
    {
        pic.preload_img = new Image()
        pic.preload_img.src = static_loc + pic.filelocation;
        rounded_epoch = roundTimestampToEpoch(pic.timestamp);

        if (!(rounded_epoch in epochs))
            epochs[rounded_epoch] = [];
        epochs[rounded_epoch].push(pic);
        epochs.order.push(rounded_epoch);
    }

    // remove duplicates, sort and return only newest items
    epochs.order = epochs.order.filter(function (date, i, array) { return array.indexOf(date) === i; })
                                     .sort()
                                     .slice(-32);

    if (epochs.order.length != 0)
    {
      for (const epoch of epochs.order)
      {
        var row = new_tbody.insertRow(new_tbody.rows.length);
        var cell = row.insertCell(0);
        var innerDiv = document.createElement('div');

        innerDiv.setAttribute("onmouseover", "anim_image(" + epoch + ")");
        innerDiv.setAttribute("id", "cam_txt_" + epoch);
        innerDiv.setAttribute("style", "color: rgb(0, 0, 255); cursor: pointer; display: flex");

        var date = new Date(epoch);
        date_contents = date.getDate() + "." + (date.getMonth()+1) + " " + addZero(date.getHours()) + ":" + addZero(date.getMinutes())

        date_div = document.createElement('div');
        date_div.setAttribute("style", "flex-grow: 1");
        date_div.innerHTML = date_contents;
        innerDiv.appendChild(date_div);

        //status_contents = '&nbsp;<img src="' + static_loc + 'loading.gif">'
        //status_div = document.createElement('div');
        //status_div.setAttribute("style", "flex-grow: 1");
        //status_div.innerHTML = status_contents;
        //innerDiv.appendChild(status_div);

        cell.appendChild(innerDiv);

        //preload_img[cam_id][i].my_id = i
        //preload_img[cam_id][i].addEventListener("load", function(event)
        //{
        //  var target = event.target || event.srcElement;
        //  var div = document.getElementById("cam" + cam_id + "_txt_" + target.my_id).getElementsByTagName('div');
        //  div[1].innerHTML = '&nbsp;<img src="' + static_loc + 'ready.gif"></div>'
        //});
      }

      last_valid_start = new Date(epochs.order[0]);
      last_valid_end = new Date(epochs.order.slice(-1)[0]);
      document.getElementById("cam_timespan").innerHTML =
        addZero(last_valid_start.getHours()) + ":" + addZero(last_valid_start.getMinutes()) + " - " +
        addZero(last_valid_end.getHours()) + ":" + addZero(last_valid_end.getMinutes());

      old_tbody.parentNode.replaceChild(new_tbody, old_tbody);
      anim_image(epochs.order.slice(-1)[0]);
    }
    else
    {
      var row = new_tbody.insertRow(new_tbody.rows.length);
      var cell = row.insertCell(0);
      var innerDiv = document.createElement('div');
      innerDiv.innerHTML = "ajanjaksolle ei löydy kuvia";
      cell.appendChild(innerDiv);
      document.getElementById("cam_timespan").innerHTML = "-";
      old_tbody.parentNode.replaceChild(new_tbody, old_tbody);
    }
  }

  // Adds a header row to the table and returns the set of columns.
  // Need to do union of keys from all records as some records may not contain
  // all records
  function addAllColumnHeaders(data, selector)
  {
    var columnSet = [];
    var headerTr$ = $('<tr/>');

    for (var i = 0 ; i < data.length ; i++) {
      var rowHash = data[i];
      for (var key in rowHash) {
        if ($.inArray(key, columnSet) == -1){
          columnSet.push(key);
          headerTr$.append($('<th/>').html(key));
        }
      }
    }
    $(selector).append(headerTr$);

    return columnSet;
  }

  // Builds the HTML Table out of data
  function buildHtmlTable(data, selector)
  {
    var columns = addAllColumnHeaders(data, selector);

    for (var i = 0 ; i < data.length ; i++) {
      var row$ = $('<tr/>');
      for (var colIndex = 0 ; colIndex < columns.length ; colIndex++) {
        var cellValue = data[i][columns[colIndex]];

        if (cellValue == null)
        {
          cellValue = "";
        }
        else if (colIndex == 0)
        {
          var aTag = $('<a>', {href: 'movement?start=' + cellValue});
          aTag.text(cellValue);
          cellValue = aTag;
        }

        row$.append($('<td/>').html(cellValue));
      }

      $(selector).append(row$);
    }
  }
