$(document).ready(function () {

    // === Load products from backend ===
    let products = [];
    $.get("/getProducts", function (data) {
        products = data;
        $(".cart-product").each(function () {
            populateProductDropdown($(this));
        });
    });

    function populateProductDropdown(dropdown) {
        dropdown.empty();
        dropdown.append(`<option value="">-- Select Product --</option>`);
        products.forEach(function (p) {
            dropdown.append(
  `<option value="${p.product_id}" data-price="${p.price_per_unit}">${p.name} (${p.uom_name})</option>`
);

        });
    }

    // === Add product row ===
    $("#addMoreButton").click(function () {
        var productBox = $(".product-box.hidden").clone();
        productBox.removeClass("hidden");

        // Populate dropdown for new row
        populateProductDropdown(productBox.find(".cart-product"));

        $("#itemsInOrder").append(productBox);
    });

    // === Remove product row ===
    $(document).on("click", ".remove-row", function () {
        $(this).closest(".product-item").remove();
        calculateGrandTotal();
    });

    // === Auto-update price when selecting a product ===
    $(document).on("change", ".cart-product", function () {
        let price = $(this).find(":selected").data("price") || 0;
        let row = $(this).closest(".product-item");
        row.find(".product-price").val(price);
        row.find(".product-qty").val(1).trigger("input"); // set qty = 1 by default
    });

    // === Update item total when qty/price changes ===
    $(document).on("input", ".product-qty, .product-price", function () {
        var row = $(this).closest(".product-item");
        var price = parseFloat(row.find(".product-price").val()) || 0;
        var qty = parseInt(row.find(".product-qty").val()) || 0;
        var total = price * qty;
        row.find(".product-total").val(total.toFixed(2));
        calculateGrandTotal();
    });

    // === Calculate grand total ===
    function calculateGrandTotal() {
        var grandTotal = 0;
        $(".product-total").each(function () {
            var val = parseFloat($(this).val()) || 0;
            grandTotal += val;
        });
        $("#product_grand_total").val(grandTotal.toFixed(2));
    }

    // === Save Order ===
    $("#saveOrder").click(function () {
        let customerName = $("#customerName").val().trim();
        let customerPhone = $("#customerPhone").val().trim();

        if (customerName === "" || customerPhone === "") {
            alert("Please enter customer name & phone.");
            return;
        }

        let orderItems = [];
        $("#itemsInOrder .product-item").each(function () {
            let productId = $(this).find(".cart-product").val();
            let qty = parseInt($(this).find(".product-qty").val()) || 0;

            if (productId && qty > 0) {
                orderItems.push({
                    product_id: productId,
                    quantity: qty
                });
            }
        });

        let grandTotal = parseFloat($("#product_grand_total").val()) || 0;

        if (orderItems.length === 0) {
            alert("Please add at least one product.");
            return;
        }

        // === Prepare order object ===
        let order = {
            customer_name: customerName,
            customer_phone: customerPhone,
            grand_total: grandTotal,
            order_details: orderItems
        };

        // === Send to backend ===
        $.ajax
        ({
            url: "/insertOrder",
            type: "POST",
            data: { data: JSON.stringify(order) },  // send as form-data
            success: function (response) 
            {
                alert("Order saved successfully! Order ID: " + response.order_id);
                $("#downloadInvoice").show(); 
            },
            error: function (xhr, status, error)
            {
                console.error("Error saving order:", error);
                alert("Failed to save order.");
            }
        });

    });

    // === Download Invoice ===
    $("#downloadInvoice").click(function () {
        let { jsPDF } = window.jspdf;
        let doc = new jsPDF();

        let customerName = $("#customerName").val().trim();
        let customerPhone = $("#customerPhone").val().trim();
        let grandTotal = $("#product_grand_total").val();

        let invoiceNo = "INV-" + Date.now();
        let today = new Date();
        let dateStr = today.toLocaleDateString() + " " + today.toLocaleTimeString();

        // Header
        doc.setFontSize(18);
        doc.text("INVOICE", 90, 15);

        doc.setFontSize(12);
        doc.text("Invoice No: " + invoiceNo, 10, 30);
        doc.text("Date: " + dateStr, 10, 40);
        doc.text("Customer: " + customerName, 10, 50);
        doc.text("Phone: " + customerPhone, 10, 60);

        // Table Header
        let y = 75;
        doc.text("Product", 10, y);
        doc.text("Price", 80, y);
        doc.text("Qty", 120, y);
        doc.text("Total", 160, y);
        y += 10;

        // Table Rows
        $("#itemsInOrder .product-item").each(function () {
            let productName = $(this).find(".cart-product option:selected").text();
            let price = $(this).find(".product-price").val();
            let qty = $(this).find(".product-qty").val();
            let total = $(this).find(".product-total").val();

            if (productName && productName !== "-- Select Product --") {
                doc.text(productName, 10, y);
                doc.text(price.toString(), 80, y);
                doc.text(qty.toString(), 120, y);
                doc.text(total.toString(), 160, y);
                y += 10;
            }
        });

        y += 10;
        doc.setFontSize(14);
        doc.text("Grand Total: " + grandTotal + " Rs", 10, y);

        doc.save(invoiceNo + ".pdf");
    });

});
