using System.Collections.Generic;
using UnityEngine;

public class BotSpawnManager : MonoBehaviour
{
  [SerializeField] private GameObject botPrefab;
  [SerializeField] private int botCount = 49;
  [SerializeField] private Vector2 dropBounds = new Vector2(300f, 300f);
  [SerializeField] private float dropAltitude = 120f;
  [SerializeField] private Transform botParent;

  private readonly List<ParachuteController> spawnedBots = new List<ParachuteController>();

  public void SpawnBots()
  {
    ClearBots();

    for (int i = 0; i < botCount; i++)
    {
      Vector3 spawnPosition = new Vector3(
        Random.Range(-dropBounds.x, dropBounds.x),
        dropAltitude,
        Random.Range(-dropBounds.y, dropBounds.y)
      );

      GameObject bot = Instantiate(botPrefab, spawnPosition, Quaternion.identity, botParent);
      ParachuteController parachute = bot.GetComponent<ParachuteController>();
      if (parachute != null)
      {
        parachute.BeginDrop(Random.Range(0.5f, 4f));
        spawnedBots.Add(parachute);
      }
    }
  }

  public void TriggerBotDrops()
  {
    foreach (ParachuteController bot in spawnedBots)
    {
      if (bot != null)
      {
        bot.ForceOpenParachute();
      }
    }
  }

  private void ClearBots()
  {
    foreach (ParachuteController bot in spawnedBots)
    {
      if (bot != null)
      {
        Destroy(bot.gameObject);
      }
    }

    spawnedBots.Clear();
  }
}
