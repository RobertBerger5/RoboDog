package com.bergerrob.robodog

import android.Manifest
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Bundle
import android.view.Menu
import android.view.MenuItem
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.fragment.app.Fragment
import androidx.fragment.app.FragmentManager
import kotlinx.android.synthetic.main.activity_startup.*
import java.net.Socket

class Startup : AppCompatActivity(),SpeechFragment.SpeechInterface{

    private val sharedPrefFile = "stocAppPrefs"

    override fun onAttachFragment(fragment: Fragment) {
        if (fragment is SpeechFragment) {
            //set callback for event
            fragment.setOnNewTextThing(this)
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        setTheme(R.style.AppTheme_NoActionBar)
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_startup)
        setSupportActionBar(toolbar)

        supportFragmentManager
            .beginTransaction()
            .add(R.id.startup_container,SocketFragment(),"socket")
            .add(R.id.startup_container, SpeechFragment(),"speech")
            .commit()

        mPreferences = getSharedPreferences(sharedPrefFile, Context.MODE_PRIVATE)

        if (ContextCompat.checkSelfPermission(
                this,
                Manifest.permission.RECORD_AUDIO
            ) != PackageManager.PERMISSION_GRANTED
        ) {
            requestPermissions(arrayOf(Manifest.permission.RECORD_AUDIO), 1)
        }

    }

    override fun onCreateOptionsMenu(menu: Menu): Boolean {
        menuInflater.inflate(R.menu.menu_startup, menu)
        return true
    }

    override fun onPause() {
        super.onPause()
    }

    override fun onNewText(msg:String){ //new text from speech button
        var sock=supportFragmentManager.findFragmentByTag("socket") as SocketFragment
        sock.sendThings(msg)
    }
}
