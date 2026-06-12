using UnityEngine;

public class CameraFollow : MonoBehaviour
{
  [SerializeField] private Transform target;
  [SerializeField] private Vector3 offset = new Vector3(0f, 2f, -4f);
  [SerializeField] private float followSmoothing = 8f;

  private void LateUpdate()
  {
    if (target == null)
    {
      return;
    }

    Vector3 desiredPosition = target.TransformPoint(offset);
    transform.position = Vector3.Lerp(transform.position, desiredPosition, followSmoothing * Time.deltaTime);
    transform.LookAt(target.position + Vector3.up * 1.5f);
  }
}
