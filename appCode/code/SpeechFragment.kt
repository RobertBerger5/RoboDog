package com.bergerrob.robodog

import android.content.Intent
import android.content.res.ColorStateList
import android.graphics.Color
import android.os.Bundle
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.TextView
import androidx.core.content.res.ResourcesCompat
import androidx.fragment.app.Fragment


class SpeechFragment : Fragment(), RecognitionListener {
    private var sr: SpeechRecognizer? = null
    lateinit var speechText: TextView
    lateinit var speechButton: Button
    lateinit internal var callback: SpeechInterface

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        sr = SpeechRecognizer.createSpeechRecognizer(this.context)
        sr!!.setRecognitionListener(this)//this activity is the listener

    }

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {

        val thisView = inflater.inflate(R.layout.fragment_speech, container, false)
        speechText = thisView.findViewById<View>(R.id.speechText) as TextView
        speechButton = thisView.findViewById<View>(R.id.speechButton) as Button
        speechButton.setOnClickListener {
            startListening()
        }

        speechButton.backgroundTintList = ColorStateList.valueOf(ResourcesCompat.getColor(resources,R.color.buttonGray,null))
        speechText.setBackgroundColor(0xfffafafa.toInt())

        // Inflate the layout for this fragment
        return thisView
    }


    //App is ready for the user to speak
    override fun onReadyForSpeech(params: Bundle) {
        speechButton.backgroundTintList = ColorStateList.valueOf(ResourcesCompat.getColor(resources,R.color.buttonGreen,null))
    }

    //user has begun to speak
    override fun onBeginningOfSpeech() {
        speechButton.backgroundTintList = ColorStateList.valueOf(ResourcesCompat.getColor(resources,R.color.buttonYellow,null))
    }

    //change in volume (I believe, haven't read much on this)
    override fun onRmsChanged(rmsdB: Float) {
        //don't bother
    }

    //buffer received (was never triggered in all my testing)
    override fun onBufferReceived(buffer: ByteArray) {
        //don't bother
    }

    //it's been a while since they talked, they're done
    override fun onEndOfSpeech() {
        speechButton.backgroundTintList = ColorStateList.valueOf(ResourcesCompat.getColor(resources,R.color.buttonGray,null))

    }

    //something went wrong
    override fun onError(error: Int) {
        val errorString: String = when (error) {
            SpeechRecognizer.ERROR_AUDIO -> "ERROR_AUDIO"
            SpeechRecognizer.ERROR_CLIENT -> "ERROR_CLIENT"
            SpeechRecognizer.ERROR_INSUFFICIENT_PERMISSIONS -> "ERROR+INSUFFICIENT_PERMISSIONS"
            SpeechRecognizer.ERROR_NETWORK -> "ERROR_NETWORK"
            SpeechRecognizer.ERROR_NETWORK_TIMEOUT -> "ERROR_NETWORK_TIMEOUT"
            SpeechRecognizer.ERROR_NO_MATCH -> "ERROR_NO_MATCH"
            SpeechRecognizer.ERROR_RECOGNIZER_BUSY -> "ERROR_RECOGNIZER_BUSY"
            SpeechRecognizer.ERROR_SERVER -> "ERROR_SERVER"
            SpeechRecognizer.ERROR_SPEECH_TIMEOUT -> "ERROR_SPEECH_TIMEOUT"
            else -> {
                "ERROR_IF_YOU_SEE_THIS_SOMETHING_HAS_GONE_HORRIBLY_WRONG"
            }
        }

        println("ERROR $error")
        speechText.text = errorString
        //sr!!.stopListening()
        //not sure if this is how you're supposed to do it, but it works!
        onBeginningOfSpeech()
        onEndOfSpeech()
    }

    //speech has been processed, here are the results
    override fun onResults(results: Bundle) {
        val result = mutableListOf<String>().apply {
            (results.get(SpeechRecognizer.RESULTS_RECOGNITION) as List<*>).forEach {
                this.add(it as String)
            }
        }
        //TODO: search for "good boy" or "bad dog" in the first couple results, also probably "play dead"
        println("Possible results: $result")
        var message:String=result[0]
        if(message.substring(message.length-3,message.length)=="dog"){
            message="bad dog"
        }else if(message.substring(message.length-3,message.length)=="boy"){
            message="good boy"
        }
        speechText.text = message//Main one, the one it's most confident about...
        message=message.replace("\\s".toRegex(),"")
        callback.onNewText(message)
    }

    //partial results? I never ran into these but maybe if it was interrupted?
    override fun onPartialResults(partialResults: Bundle) {
        val result = mutableListOf<String>().apply {
            (partialResults.get(SpeechRecognizer.RESULTS_RECOGNITION) as List<*>).forEach {
                this.add(it as String)
            }
        } //copy pasted from above
        println("partial results: $result")
    }

    //vague event I guess?
    override fun onEvent(eventType: Int, params: Bundle) {
        println("there's been an event")
    }

    private fun startListening() {
        speechButton.backgroundTintList = ColorStateList.valueOf(ResourcesCompat.getColor(resources,R.color.buttonRed,null))
        val speechIntent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
        speechIntent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
        sr!!.startListening(speechIntent)
    }

    fun setOnNewTextThing(callback: SpeechInterface) {
        this.callback = callback
    }

    interface SpeechInterface{
        fun onNewText(msg:String)
    }
}
