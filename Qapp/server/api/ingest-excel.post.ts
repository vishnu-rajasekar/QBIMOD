// app/server/api/ingest-excel.post.ts
import { defineEventHandler, readBody } from 'h3'
import { SpeckleClient } from '@speckle/speckle-client'

export default defineEventHandler(async (event) => {
  try {
    // 1. Parse incoming JSON body
    const { rows } = await readBody(event)
    if (!rows || !rows.length) {
      return { error: 'No rows provided' }
    }

    // 2. Get Speckle credentials from runtime config
    const config = useRuntimeConfig()
    const token = config.speckleToken
    const streamId = config.speckleStreamId
    const serverUrl = config.speckleServerUrl || 'https://speckle.xyz'

    // 3. Initialize Speckle Client
    const client = new SpeckleClient()
    client.serverUrl = serverUrl
    await client.authenticate(token)

    // 4. Build an array of Speckle objects from the Excel rows
    const headers = Object.keys(rows[0])
    const speckleObjects = rows.map((row: Record<string, any>) => {
      const obj: Record<string, any> = { speckle_type: 'Objects.CustomData' }
      for (const h of headers) {
        obj[h] = row[h]
      }
      return obj
    })

    // 5. Create a “root object” containing the array
    const rootObject = {
      speckle_type: 'Objects.CustomData',
      rows: speckleObjects,
    }

    // 6. Send data to Speckle (create the object, then create a commit)
    const objectId = await client.object.create(streamId, rootObject)
    const commit = await client.commit.create({
      streamId,
      objectId,
      branchName: 'main',
      message: 'Excel data commit from Nuxt 3',
    })

    return { commitId: commit.id, message: 'Data successfully sent to Speckle!' }
  } catch (err: any) {
    console.error(err)
    return { error: err.message || 'Unknown error' }
  }
})
