package com.itschool.babydinocoloring

import com.amazon.device.iap.PurchasingListener
import com.amazon.device.iap.PurchasingService
import com.amazon.device.iap.model.FulfillmentResult
import com.amazon.device.iap.model.ProductDataResponse
import com.amazon.device.iap.model.PurchaseResponse
import com.amazon.device.iap.model.PurchaseUpdatesResponse
import com.amazon.device.iap.model.UserDataResponse
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel

class MainActivity : FlutterActivity() {

    private var channel: MethodChannel? = null
    private val unlockSku = "full_library_unlock"

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        channel = MethodChannel(
            flutterEngine.dartExecutor.binaryMessenger,
            "com.itschool.babydinocoloring/iap"
        )
        channel?.setMethodCallHandler { call, result ->
            when (call.method) {
                "init" -> {
                    registerListener()
                    result.success(null)
                }
                "getProductData" -> {
                    val sku = call.argument<String>("sku") ?: unlockSku
                    PurchasingService.getProductData(hashSetOf(sku))
                    result.success(null)
                }
                "purchase" -> {
                    // Always send the REAL purchase call; never short-circuit
                    // from a cached flag. Report only Amazon's response.
                    val sku = call.argument<String>("sku") ?: unlockSku
                    PurchasingService.purchase(sku)
                    result.success(null)
                }
                "getPurchaseUpdates" -> {
                    PurchasingService.getPurchaseUpdates(true)
                    result.success(null)
                }
                else -> result.notImplemented()
            }
        }
    }

    // Re-register the listener on EVERY onStart (Amazon requirement; the
    // listener can be lost when the activity is recreated).
    override fun onStart() {
        super.onStart()
        registerListener()
    }

    override fun onResume() {
        super.onResume()
        registerListener()
        // Warm up + verify the SKU and refresh receipts on every resume.
        PurchasingService.getProductData(hashSetOf(unlockSku))
        PurchasingService.getPurchaseUpdates(false)
    }

    private fun registerListener() {
        try {
            PurchasingService.registerListener(applicationContext, purchasingListener)
            notifyListenerStatus("registered")
        } catch (e: Exception) {
            notifyListenerStatus("error: ${e.message}")
        }
    }

    private fun notifyListenerStatus(status: String) {
        runOnUiThread {
            channel?.invokeMethod("onListenerStatus", mapOf("status" to status))
        }
    }

    private val purchasingListener = object : PurchasingListener {

        override fun onUserDataResponse(response: UserDataResponse) {
            // Not needed for a single entitlement, but part of the interface.
        }

        override fun onProductDataResponse(response: ProductDataResponse) {
            val status = response.requestStatus?.name ?: "UNKNOWN"
            var price = ""
            var found = false
            if (response.requestStatus == ProductDataResponse.RequestStatus.SUCCESSFUL) {
                val product = response.productData[unlockSku]
                if (product != null) {
                    found = true
                    price = product.price ?: ""
                }
            }
            runOnUiThread {
                channel?.invokeMethod(
                    "onProductData",
                    mapOf("status" to status, "price" to price, "found" to found)
                )
            }
        }

        override fun onPurchaseResponse(response: PurchaseResponse) {
            val status = response.requestStatus?.name ?: "UNKNOWN"
            if (response.requestStatus == PurchaseResponse.RequestStatus.SUCCESSFUL) {
                val receipt = response.receipt
                if (receipt != null && !receipt.isCanceled) {
                    // Grant content, then ALWAYS notify fulfillment.
                    PurchasingService.notifyFulfillment(
                        receipt.receiptId,
                        FulfillmentResult.FULFILLED
                    )
                }
            }
            runOnUiThread {
                channel?.invokeMethod("onPurchase", mapOf("status" to status))
            }
        }

        override fun onPurchaseUpdatesResponse(response: PurchaseUpdatesResponse) {
            val status = response.requestStatus?.name ?: "UNKNOWN"
            var owned = false
            if (response.requestStatus ==
                PurchaseUpdatesResponse.RequestStatus.SUCCESSFUL
            ) {
                for (receipt in response.receipts) {
                    if (receipt.sku == unlockSku && !receipt.isCanceled) {
                        owned = true
                        PurchasingService.notifyFulfillment(
                            receipt.receiptId,
                            FulfillmentResult.FULFILLED
                        )
                    }
                }
                if (response.hasMore()) {
                    PurchasingService.getPurchaseUpdates(false)
                }
            }
            runOnUiThread {
                channel?.invokeMethod(
                    "onPurchaseUpdates",
                    mapOf("status" to status, "owned" to owned)
                )
            }
        }
    }
}
