package com.bergerrob.robodog

import android.content.Intent
import android.content.res.ColorStateList
import android.graphics.Color
import android.os.Bundle
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.text.Editable
import android.text.TextWatcher
import android.view.KeyEvent
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.core.content.ContextCompat
import androidx.core.content.res.ResourcesCompat
import androidx.fragment.app.Fragment
import kotlin.concurrent.fixedRateTimer


class SocketFragment : Fragment(){
    lateinit var socketButton: Button
    lateinit var ipText:EditText
    lateinit var socket:SocketThread
    var connected:Boolean=false//unused so far, could be a disconnect button?
    var ipaddr:String=""

    /*override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
    }*/

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {

        val thisView = inflater.inflate(R.layout.fragment_socket, container, false)
        ipText=thisView.findViewById<View>(R.id.IPText) as EditText
        socketButton = thisView.findViewById<View>(R.id.socketButton) as Button
        socketButton.setOnClickListener {
            try {
                //if there's already a socket, disconnect it
                if(::socket.isInitialized) {
                    synchronized(socket.lock) {
                        socket.message = "disconnect"
                        (socket.lock as java.lang.Object).notify()
                    }
                }
                socket = SocketThread(ipText.text.toString(), 50000)
                socket.start()
            }catch(e:Error){
                System.out.println("ERROR: whoops.")
            }
        }

        socketButton.backgroundTintList = ColorStateList.valueOf(ResourcesCompat.getColor(resources,R.color.buttonGray,null))

        //wasn't sure how else to do it, just check the connection status every second
        fixedRateTimer("default", false, 0L, 100){
            if(!::socket.isInitialized){
                socketButton.backgroundTintList=ColorStateList.valueOf(ResourcesCompat.getColor(resources,R.color.buttonGray,null))
            }else{
                val col:Int=when(socket.status){
                    SocketThread.Status.DISCONNECTED-> ResourcesCompat.getColor(resources,R.color.buttonGray,null)//ColorStateList.valueOf(Color.GRAY)
                    SocketThread.Status.CONNECTING->ResourcesCompat.getColor(resources,R.color.buttonYellow,null)//ColorStateList.valueOf(Color.YELLOW)
                    SocketThread.Status.CONNECTED->ResourcesCompat.getColor(resources,R.color.buttonGreen,null)//ColorStateList.valueOf(Color.GREEN)
                    SocketThread.Status.ERROR_HOST,SocketThread.Status.ERROR_IO->ResourcesCompat.getColor(resources,R.color.buttonRed,null)//ColorStateList.valueOf(Color.RED)
                    else->ResourcesCompat.getColor(resources,R.color.colorPrimaryDark,null)//ColorStateList.valueOf(Color.WHITE)
                }
                socketButton.backgroundTintList=ColorStateList.valueOf(col)
                connected=(socket.status==SocketThread.Status.CONNECTED)
                /*if(socket!=null) {
                    socket.updateStatus() //how is socket a null object reference here??
                }*/
            }
        }

        // Inflate the layout for this fragment
        return thisView
    }

    /*override fun onStop() {
        super.onStop()
        //socket.disconnect()
    }*/
    override fun onPause() {
        super.onPause()
        try{
            synchronized(socket.lock){
                socket.message="disconnect"
                (socket.lock as java.lang.Object).notify()
            }
        }catch(e:Exception){

        }
        ipaddr=ipText.text.toString() //sometimes it forgets the ip they had entered, remember it until the app closes for real
    }

    override fun onResume() {
        super.onResume()
        ipText.setText(ipaddr)
    }

    fun sendThings(msg:String){
        try{
            synchronized (socket.lock) {
                socket.message = msg
                (socket.lock as java.lang.Object).notify()
            }
        }catch(e:Error){
            //socketText.text=socket.getThreadStatus()
            //socketText.timportext="ERROR! Are you sure you're connected to the server?"
        }
    }
}
