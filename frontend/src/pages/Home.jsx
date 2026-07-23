import React from 'react'
import { HandleDisplay } from '../components/HandleDisplay'

export default function Home({app}) {
  return (
    <>
      <h1 className="title">{app}</h1>
      <div className="box2">
        <p></p>
        <p><HandleDisplay user={{username:'admin', rank:'admin'}} /></p>
        <p><HandleDisplay user={{username:'mod', rank:'mod'}} /></p>
        <p><HandleDisplay user={{username:'vip', rank:'vip'}} /></p>
        <p><HandleDisplay user={{username:'pro', rank:'pro'}} /></p>
        <p><HandleDisplay user={{username:'gold', rank:'gold'}} /></p>
        <p><HandleDisplay user={{username:'member', rank:'member'}} /></p>
      </div>
    </>
  )
}
