(function ($) {
  jQuery(document).ready(function ($) {
    $(".dynamicTable[data-ajax-endpoint]").each(function (i, v) {

      function createTable(tableWrapper) {
        var classes = "";
        var classesThead = "";
        if ($(tableWrapper).attr("data-classes")) {
          classes = " class=\"" + $(tableWrapper).attr("data-classes") + "\"";
        }
        if ($(tableWrapper).attr("data-classes-thead")) {
          classesThead = " class=\"" + $(tableWrapper).attr("data-classes-thead") + "\"";
        }
        $(tableWrapper).html(
          "<div class=\"table-options\"><div class=\"dropdown results-per-page\"><button class=\"btn btn-light btn-outline-secondary btn-sm dropdown-toggle\" type=\"button\" id=\"dropdownMenuButton\" data-toggle=\"dropdown\" aria-haspopup=\"true\" aria-expanded=\"false\"/><div class=\"dropdown-menu\" aria-labelledby=\"dropdownMenuButton\"></div></div><div class=\"ajaxPagination\"></div></div><table" + classes + "><thead" + classesThead + "></head><tbody></tbody></table><div class=\"table-options\"><div class=\"dropdown results-per-page\"><button class=\"btn btn-light btn-outline-secondary btn-sm dropdown-toggle\" type=\"button\" id=\"dropdownMenuButton\" data-toggle=\"dropdown\" aria-haspopup=\"true\" aria-expanded=\"false\"/><div class=\"dropdown-menu\" aria-labelledby=\"dropdownMenuButton\"></div></div><div class=\"ajaxPagination\"></div></div>");
      }

      function generateHeading(data) {
        console.log(data);
        if (data["order_setable"]) {
          return "<th>" + data["name"] + "<i class=\"fa fa-sort-" + data["order"] + "\" aria-hidden=\"true\"></i></th>";
        }
        else {
          return "<th>" + data["name"] + "</th>";
        }
      }

      function generateRow(data) {
        return "<tr><td>" + data.join("</td><td>") + "</td></tr>";
      }

      function getRequestData(tableWrapper) {
        var data = {};
        if ($(tableWrapper).attr("data-ajaxdata-per-page")) {
          data["per_page"] = $(tableWrapper).attr("data-ajaxdata-per-page");
        }
        if ($(tableWrapper).attr("data-ajaxdata-start")) {
          data["start"] = $(tableWrapper).attr("data-ajaxdata-start");
        }
        return data;
      }

      function generatePaginationLi(url, text, linkAttr = "", classes = "page-item") {
        linkAttr = linkAttr == "" ? linkAttr : " " + linkAttr;
        return "<li class=\"" + classes + "\"><a class=\"page-link\" href=\"" + url + "\"" + linkAttr + ">" + text + "</a></li>";
      }

      function generatePagination(info) {
        var pageCountRange = 5;
        var out = "<nav aria-label=\"Page navigation\"><ul class=\"pagination pagination-sm\">";
        //Prev
        if (info["current_start"] != 0) {
          out += generatePaginationLi("#",
            "<span aria-hidden=\"true\">&laquo;</span><span class=\"sr-only\">Previous</span>",
            " aria-label=\"Previous\" data-page=\"0\"");
        }

        var pageCount = info["count_total"] / info["per_page"];
        var current_page = info["current_start"] / info["per_page"];
        var pageStart = Math.max(0, current_page - pageCountRange);
        var page = info["per_page"] * pageStart;

        for (var i = pageStart; i < Math.min(pageCount, current_page + pageCountRange); i++) {
          out += generatePaginationLi("#",
            (i + 1) + (i == current_page ? "<span class=\"sr-only\">(current)</span>" : ""),
            " data-page=\"" + page + "\"", i == current_page ? "page-item active" : "page-item");
          page += info["per_page"];
        }


        // Next
        if (current_page + 1 < pageCount) {
          out += generatePaginationLi("#",
            "<span aria-hidden=\"true\">&raquo;</span><span class=\"sr-only\">Next</span>",
            " aria-label=\"Next\" data-page=\"" + ((current_page + 1 ) * info["per_page"]) + "\"");
        }


        return out + "</ul></nav>";
      }

      function updateContent(tableWrapper, url) {
        var data = getRequestData(tableWrapper);
        $.ajax({
          dataType: "json",
          url: url,
          data: data,
          success: function (data) {

            if (!$(tableWrapper).find("table").length) {
              createTable(tableWrapper);
            }
            var headings = "";
            for (var i in data["headers"]) {
              headings += generateHeading(data["headers"][i]);
            }
            var rows = "";
            for (var i in data["body"]) {
              rows += generateRow(data["body"][i]);
            }
            $(tableWrapper).attr("data-ajaxdata-per-page", data["info"]["per_page"]);
            $(tableWrapper).attr("data-ajaxdata-start", data["info"]["current_start"]);

            var pagination = generatePagination(data["info"]);
            $(tableWrapper).find(".table-options .results-per-page").each(function (i, v) {
              var possibleResultsPerPage = data["info"]["possible_results_per_page"];
              var out = possibleResultsPerPage.join("</a><a class=\"dropdown-item\" href=\"#\">");

              if (out !== "") {
                out = "<a class=\"dropdown-item\" href=\"#\">" + out + "</a>";
              }
              $(v).find(".dropdown-menu").html(out);
              $(v).find("button.btn").html(data["info"]["per_page"]);
              $(v).find(".dropdown-item").click(function (e) {
                e.preventDefault();
                $(tableWrapper).attr("data-ajaxdata-per-page", $(this).text());
                updateContent(tableWrapper, url);
              });

            });
            $(tableWrapper).find("table thead").html(headings);
            $(tableWrapper).find("table tbody").html(rows);
            $(tableWrapper).find(".ajaxPagination").each(function (i, v) {
              $(v).html(pagination);
              $(v).find("a").click(function (e) {
                e.preventDefault();
                $(tableWrapper).attr("data-ajaxdata-start", $(this).attr("data-page"));
                updateContent(tableWrapper, url);
              });
            });
          }
        });
      }

      updateContent(v, $(v).attr("data-ajax-endpoint"));

      if ($(v).attr("data-ajax-refresh-time")) {
        setInterval(function () {
          updateContent(v, $(v).attr("data-ajax-endpoint"))
        }, $(v).attr("data-ajax-refresh-time"));
      }
    });
  });

  $("select[data-dynamic-description=\"true\"]").each(function (i, v) {
    function setDescription(select) {
      select.attr("aria-describedby", "description-" + select.val());
      select.parent().find(".descriptions>div").hide(0);
      select.parent().find(".descriptions div[data-description-for=\"" + select.val() + "\"]").fadeIn("slow");

    }

    setDescription($(this));

    $(this).change(function () {
      setDescription($(this));
    });

  });
})(jQuery);
