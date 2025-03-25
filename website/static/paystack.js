// paystack.js

document.addEventListener("DOMContentLoaded", function () {
  const paymentForm = document.getElementById("formWrapper");
  paymentForm.addEventListener("submit", payWithPaystack, false);

  function payWithPaystack(e) {
    e.preventDefault();
    const email = "{{ email }}";
    const ksceIndex = "{{ ksce_index }}";

    const handler = PaystackPop.setup({
      key: "pk_live_4844d97cb41c83140c5826cac03264051c0379d9",
      email: email,
      amount: 400, // Amount in kobo (300 kobo = 3 KES)
      currency: "KES", // Set currency to Kenyan Shilling
      channels: ["mobile_money", "card"], // Specify available payment channels
      metadata: {
        custom_fields: [
          {
            display_name: "KSCE Index Number",
            variable_name: "ksce_index_number",
            value: ksceIndex,
          },
        ],
      },
      callback: function (response) {
        try {
          const reference = response.reference;
          // Redirect to the verify-payment route with the reference
          window.location.href = `/payments/verify-payment?reference=${reference}&email=${encodeURIComponent(
            email
          )}&ksceIndex=${encodeURIComponent(ksceIndex)}`;
        } catch (error) {
          console.error("Error during callback:", error);
          alert("An error occurred. Please try again.");
        }
      },
      onClose: function () {
        // Optional: You can handle the close event if needed
      },
    });
    handler.openIframe();
  }
});
